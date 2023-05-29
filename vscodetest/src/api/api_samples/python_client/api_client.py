import requests
import json


class CloudBoltAPIClient(object):
    def __init__(
        self,
        username,
        password,
        host="localhost",
        port=443,
        protocol="https",
        verify=False,
        cert=None,
        **kwargs,
    ):
        """
        Creates base URL and auth required for REST calls.
        """
        self.BASE_URL = "{protocol}://{host}:{port}/api/".format(
            protocol=protocol, host=host, port=port
        )
        self.verify = verify
        self.cert = cert

        self.auth_dict = {
            "username": username,
            "password": password,
        }
        two_factor_token = kwargs.get("token", None)
        domain = kwargs.get("domain", None)
        if two_factor_token:
            self.auth_dict["token"] = two_factor_token
        if domain:
            self.auth_dict["domain"] = domain

        self.create_api_token()

    def create_api_token(self):
        self.api_token = None
        auth_url = self._fix_url("/api/v2/api-token-auth/")
        content = self._post_request(auth_url, body=json.dumps(self.auth_dict))
        api_token_return = json.loads(content)
        if "token" in api_token_return:
            self.api_token = api_token_return["token"]
        elif "detail" in api_token_return:
            raise Exception(
                "Failed to get API token: {error}".format(
                    error=api_token_return["detail"]
                )
            )
        else:
            raise Exception(
                "No API token in response: {content}".format(content=content)
            )

    def _get_request_kwargs(self):
        request_kwargs = {
            "verify": self.verify,
            "allow_redirects": False,
        }
        if self.cert is not None:
            request_kwargs["cert"] = self.cert
        return request_kwargs

    def _update_headers(self, request_kwargs):
        headers = request_kwargs.get("headers") or {}
        if not request_kwargs.get("files"):
            # By default, requests should be parsed as JSON; however do not set
            # this for file uploads or they'll break.
            headers["Content-Type"] = "application/json"
        if self.api_token:
            headers["Authorization"] = "Bearer {token}".format(token=self.api_token)
        request_kwargs["headers"] = headers

    def _request(self, method, url):
        """
        Make a request of the specified method and return the text response.
        """
        request_kwargs = self._get_request_kwargs()
        self._update_headers(request_kwargs)
        response = requests.request(method, url, **request_kwargs)
        if response.status_code == 401:
            # Token may have expired, create a new one and try one more time
            self.create_api_token()
            self._update_headers(request_kwargs)
            response = requests.request(method, url, **request_kwargs)
        return response.text

    def _post_request(self, url, body="", headers=None, files=None):
        request_kwargs = self._get_request_kwargs()
        request_kwargs.update({"data": body, "files": files})
        self._update_headers(request_kwargs)
        response = requests.post(url, **request_kwargs)
        if 300 <= response.status_code < 400:
            raise requests.HTTPError(
                "The CloudBolt API client does not follow redirects, and a {} "
                "status code was returned".format(response.status_code),
                response=response,
            )
        # raise an exception if a failure status code was returned
        response.raise_for_status()

        return response.text

    def get(self, url=""):
        """
        Simple GET entry point
        """
        url = self._fix_url(url)
        return self._request("GET", url)

    def get_raw(self, url):
        """
        Make a GET request and return the raw response object.  For more about
        that object, see:
        http://docs.python-requests.org/en/latest/api/#requests.Response.raw
        """
        url = self._fix_url(url)
        request_kwargs = self._get_request_kwargs()
        self._update_headers(request_kwargs)
        # By setting stream to True we tell the Python Requests library to
        # return the raw response.
        return requests.request("GET", url, stream=True, **request_kwargs)

    def post(self, url, body="", headers=None, files=None):
        """
        POST entry point. Creates a new API token if previous one expired.

        The POST in create_api_token doesn't use this because it could create
        infinite recursion.
        """
        url = self._fix_url(url)

        try:
            response = self._post_request(url, body, headers=headers, files=files)
        except requests.HTTPError as err:
            if err.response.status_code == 401:
                # Token may have expired, create a new one and try one more time
                self.create_api_token()
                response = self._post_request(url, body, headers=headers, files=files)
            else:
                raise
        return response

    def delete(self, url):
        """
        Simple DELETE entry point
        """
        url = self._fix_url(url)

        return self._request("DELETE", url)

    def _fix_url(self, url):
        if url.startswith("/api"):
            url = url[4:]
        split = url.split("?")
        url = split[0]
        if not url.endswith("/"):
            url = "{url}/".format(url=url)
        if url.startswith("/") and self.BASE_URL.endswith("/"):
            url = url[1:]
        args = {
            "base_url": self.BASE_URL,
            "url": url,
            "params": "?".join(split[1:] or ""),
        }
        return "{base_url}{url}?{params}".format(**args)
