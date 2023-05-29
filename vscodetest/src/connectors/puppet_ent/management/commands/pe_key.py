from __future__ import unicode_literals
from __future__ import print_function
import sys

from django.core.management import BaseCommand

from connectors.puppet_ent.exceptions import PEConfException
from connectors.puppet_ent.models import PEConf


def execute(action, conf_id):
    command = Command()
    command.handle(action, conf_id)


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        self.conf = None

    @staticmethod
    def print_usage_and_exit():
        print("usage: ./manage.py pe_key {init, req, fetch} <pe instance id>")
        sys.exit(1)

    def handle(self, *args, **options):

        if args[0] == "help":
            self.print_usage_and_exit()

        try:
            conf_id = args[1]
        except IndexError:
            raise PEConfException("PE provider ID not specified")

        self.conf = PEConf.objects.get(id=int(conf_id))

        if args[0] == "init":
            self._init_key()
        elif args[0] == "req":
            self._submit_csr()
        elif args[0] == "fetch":
            self._fetch_signed()
        else:
            Command.print_usage_and_exit()

    def _init_key(self):
        """
        Initialize SSL for PuppetEnterprise connector instance. Remove all existing SSL key
        material and replace with a new, unsigned private key.
        """
        self.conf.initialize_ssl()
        print(
            "A new private key has been generated and the ca cert has been retrieved from PE."
        )

    def _submit_csr(self):
        self.conf.submit_csr()
        print("The private key has been submitted to PE for signing by the PE admin.")

    def _fetch_signed(self):
        self.conf.fetch_signed_cert()
        print("A signed certficate has been received from PE and stored in CloudBolt.")
