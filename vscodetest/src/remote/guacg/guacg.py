#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2014 Mohab Usama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from gevent import monkey

monkey.patch_all()  # noqa

import argparse
from collections import OrderedDict
import os
import requests
import sys
import time

from django.conf import settings

import gevent
from geventwebsocket import WebSocketServer, Resource, WebSocketApplication
from guacamole.client import GuacamoleClient, PROTOCOL_NAME

DEFAULT_LISTEN_ADDRESS = "127.0.0.1"
DEFAULT_LISTEN_PORT = 6060
DEBUG = False

_memcached_namespace = None


class GuacamoleApp(WebSocketApplication):
    """
    Server-Client geventwebsocket.WebSocketApplication that runs within a
    geventwebsocket.WebSocketServer to serve up a WebSocket HTTP/WSGI server
    that listens for GuacamoleJSClient WebSocket connections and when one is
    established, sets up a connection to guacd using pyguacamole. It then acts
    as a simple proxy/tunnel between the two.
    """

    def __init__(self, ws):
        self.client = None
        self._listener = None
        self.debug = DEBUG

        """
        Set up Django settings so we can use memcache and secrets, much like wsgi.py.
        This will have to be updated if wsgi.py changes.
        This is all being done in this __init__ because it needs to have a chance
        to have parsed the args to populate _memcached_namespace.
        """
        path = "/opt"
        if path not in sys.path:
            sys.path.append(path)
        path = "/opt/cloudbolt"
        if path not in sys.path:
            sys.path.append(path)

        os.environ["DJANGO_SETTINGS_MODULE"] = "cloudbolt.settings"
        if _memcached_namespace:
            os.environ["USER"] = _memcached_namespace
        """
        End setting up Django
        """

        from django.core import signing
        from django.core.cache import cache

        self.cache = cache
        self.signing = signing

        super(GuacamoleApp, self).__init__(ws)

    def get_from_cache(self, key):
        cached_value = self.cache.get(key)
        if cached_value is None:
            return {}
        decrypted = self.signing.loads(cached_value)
        return decrypted

    def on_open(self, *args, **kwargs):
        """
        New Web socket connection opened. Instantiate and connect to guacd
        using pyguacamole. Before we connect, we check if the origin of the
        request is from an allowed host. If a cloudbolt installation does not
        have a list of allowed hosts, then CSWSH is not prevented.
        """
        if settings.ALLOWED_HOSTS == [] or settings.ALLOWED_HOSTS[0] == "*":
            pass
        else:
            try:
                request_origin_host = self.ws.origin.split("//")[1].split(":")[0]
                if request_origin_host not in settings.ALLOWED_HOSTS:
                    raise Exception(
                        "Request origin violates cross origin domain policy. Origin is {0} and allowed hosts are {1}".format(
                            request_origin_host, settings.ALLOWED_HOSTS
                        )
                    )
            except IndexError:
                raise IndexError("Invalid origin url")

        path = self.ws.environ["PATH_INFO"]
        path_parts = path.split("/")
        guacd_host = path_parts[2]
        guacd_port = path_parts[3]
        remote_host = path_parts[4]
        remote_port = path_parts[5]
        remote_protocol = path_parts[6]
        width = path_parts[7].split("x")[0]
        height = path_parts[7].split("x")[1]
        auth_scheme = path_parts[8]
        auth_host = path_parts[9]
        try:
            credentials_key = path_parts[10]
        except IndexError:
            credentials_key = None

        # Pass content into QUERY_STRING via the guacJS guac.connect(query_string).
        # Note that such content will be URI-encoded.
        # query_string = self.ws.environ['QUERY_STRING']

        # Token-based auth for websocket
        query_string = self.ws.environ.get("QUERY_STRING", "")
        token, server_id = query_string.split("&")
        token = token.replace("token=", "")
        server_id = server_id.replace("server=", "")

        if self.client:
            # we have a running client?!
            self.client.close()

        # Instantiate a Guacamole Client, passing in the guacd parameters.
        self.client = GuacamoleClient(guacd_host, guacd_port, debug=self.debug)

        client_handshake_kwargs = {
            "protocol": remote_protocol,
            "hostname": remote_host,
            "port": remote_port,
            "width": width,
            "height": height,
            "ignore_cert": "true",
        }

        if credentials_key:
            credentials = self.get_from_cache(credentials_key)

            # Fetch the credentials from memcached using this key
            # and add them to the kwargs being passed to the client
            client_handshake_kwargs["username"] = credentials.get("username")
            if "private_key" in credentials:
                client_handshake_kwargs["private_key"] = credentials.get("private_key")
                if "passphrase" in credentials:
                    client_handshake_kwargs["passphrase"] = credentials.get(
                        "passphrase"
                    )
            else:
                client_handshake_kwargs["password"] = credentials.get("password")
                client_handshake_kwargs["security"] = credentials.get("security")
                if "domain" in credentials:
                    client_handshake_kwargs["domain"] = credentials.get("domain")

        # Post to authentication endpoint
        auth_data = {"token": token, "server_id": server_id}
        response = requests.post(
            f"{auth_scheme}://{auth_host}/api/v2/remote/authenticate/",
            json=auth_data,
            verify=False,
        )
        if response.status_code != 200:
            raise Exception("Not authorized.")

        # Connect to guacd.
        self.client.handshake(**client_handshake_kwargs)
        self._start_listener()

    def on_message(self, message):
        """
        New message received on the websocket. Send it to guacd.
        """
        # send message to guacd server
        if message:
            self.client.send(message)

    def on_close(self, reason):
        """
        Websocket closed. Disconnect from guacd.
        """
        # @todo: consider reconnect from client. (network glitch?!)
        self._stop_listener()
        self.client.close()
        self.client = None

    def _start_listener(self):
        """
        Spawns a gevent client instance of guacd_listener.
        """
        if self._listener:
            self._stop_listener()
        self._listener = gevent.spawn(self.guacd_listener)
        self._listener.start()

    def _stop_listener(self):
        """
        Kills the gevent client instance of guacd_listener.
        """
        if self._listener:
            self._listener.kill()
            self._listener = None

    def guacd_listener(self):
        """
        A listener that would handle any messages sent from Guacamole server
        and push directly to browser client (over websocket).
        """
        while True:
            instruction = self.client.receive()
            self.ws.send(instruction)

    @classmethod
    def protocol_name(cls):
        """
        Return our WebSocketApplication protocol name, required by gevent-websocket.
        """
        return PROTOCOL_NAME


def run(
    listen_address=DEFAULT_LISTEN_ADDRESS,
    listen_port=DEFAULT_LISTEN_PORT,
    debug=False,
    username=None,
):
    """
    Run our websocket server with configured urls.
    """

    while True:
        print("guacg GuacamoleWebSockets<-->guacd tunnel starting...")
        try:
            server_listen = (listen_address, int(listen_port))
            resources = Resource(OrderedDict({"/ws": GuacamoleApp}))
            server = WebSocketServer(server_listen, resources, debug=debug)
            server.serve_forever()
        except Exception as e:
            print("guacg tunnel terminated abnormally, restarting...")
            print(e)
        time.sleep(5)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""
        Gevent-Guacamole is a Websocket server that acts as a broker for
        Guacamole RDP server.
        """
    )

    parser.add_argument(
        "-H",
        "--host",
        default=DEFAULT_LISTEN_ADDRESS,
        dest="host",
        help="Server host listening address.",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=DEFAULT_LISTEN_PORT,
        dest="port",
        help="Server listening port.",
    )

    parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", help="Run in debug mode"
    )

    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        default=None,
        help="Use this namespace to connect to memcached",
    )

    args = parser.parse_args()

    _memcached_namespace = args.username
    DEBUG = args.debug

    # start the server
    run(
        listen_address=args.host,
        listen_port=args.port,
        debug=DEBUG,
        username=args.username,
    )
