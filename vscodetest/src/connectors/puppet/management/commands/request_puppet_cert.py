from __future__ import unicode_literals
from __future__ import print_function
import os

from connectors.puppet.models import PuppetConf
from connectors.puppet.management.commands.base_command import BasePuppetConfCommand


# wrap the command so that we don't have to use
# django.core.management.call_command because that doesn't work when the
# connector is in pyc only format because Django doesn't find .pyc management
# commands.
def execute(conf_id):
    command = Command()
    command.handle(conf_id)


class Command(BasePuppetConfCommand):
    help = """
    Generate an SSL certificate for this CloudBolt instance and send a CSR to
    the puppet master for signing.

    Usage:

        ./manage.py request_puppet_cert puppet_conf_id

    Or run this command from a Django app:

        from django.core import management
        management.call_command('request_puppet_cert', 1)

    1. Uses cert name as determined by Puppet connector
    2. Saves the cert name on the PuppetConf
    3. Generates a 1024-bit RSA cert
    4. Generates a certificate signing request (CSR)
    5. Sends the CSR to the puppet master via HTTP PUT
    """

    def handle(self, *args, **options):
        try:
            conf_id = args[0]
        except IndexError:
            raise RuntimeError("Puppet provider ID not specified")
        puppet_conf = PuppetConf.objects.get(id=int(conf_id))

        if puppet_conf.cert_requested():
            raise RuntimeError(
                "The CSR for this Puppet provider has already been sent to "
                "the Puppet Master (hostname {}) and needs to be signed "
                "before it can be installed.".format(puppet_conf.hostname)
            )

        certname = puppet_conf.get_cert_name().lower()
        certdir = puppet_conf.get_cert_dir()
        if not os.path.exists(certdir):
            print("Creating puppet cert directory: {}".format(certdir))
            try:
                os.makedirs(certdir, mode=0o777)
                puppet_conf.cert_state = "Create Cert Directory Done"
                puppet_conf.cert_message = ""
            except IOError as e:
                puppet_conf.cert_state = "Create Cert Directory Error"
                puppet_conf.cert_message = (
                    "Failed to create certificate directory {}.\n  Output: {}"
                ).format(certdir, str(e))
            puppet_conf.save()

        self.generate_cert(puppet_conf, certdir, certname)
        self.generate_csr(puppet_conf, certdir, certname)
        self.send_csr(puppet_conf, certdir, certname, puppet_conf.hostname)

    def generate_cert(self, puppet_conf, certdir, certname):
        cmd = [
            "/usr/bin/openssl",
            "genrsa",
            "-out",
            "{}/{}.key".format(certdir, certname),
            "1024",
        ]
        self.run_cmd_and_update_state(
            cmd,
            puppet_conf,
            "Generate Cert Done",
            "Generate Cert Error",
            "Failed to generate SSL certificate.",
        )

        # At this point an artifact exists on the filesystem.  To prevent any
        # problems arising from changed hostnames or other factors affecting
        # the cert name formula, this becomes the permanent cert name for this
        # conf; puppet_conf.get_cert_name() will return it from now on instead
        # of calculating a value.
        if puppet_conf.cert_state == "Generate Cert Done":
            puppet_conf.cert_name = certname
            puppet_conf.save()

    def generate_csr(self, puppet_conf, certdir, certname):
        cmd = [
            "/usr/bin/openssl",
            "req",
            "-new",
            "-key",
            "{}/{}.key".format(certdir, certname),
            "-subj",
            "/CN={}".format(certname),
            "-out",
            "{}/{}.csr".format(certdir, certname),
        ]
        self.run_cmd_and_update_state(
            cmd,
            puppet_conf,
            "Generate CSR Done",
            "Generate CSR Error",
            "Failed to generate certificate signing request (CSR).",
        )

    def send_csr(self, puppet_conf, certdir, certname, pm_name):
        # WHY ARE WE USING CURL?
        # WE HAVE REQUESTS RIGHT?!?
        cmd = [
            "curl",
            "-k",
            "-X",
            "PUT",
            "-H",
            "Content-Type:text/plain",
            "--data-binary",
            "@{}/{}.csr".format(certdir, certname),
            "https://{}:8140/production/certificate_request/{}".format(
                pm_name, certname
            ),
        ]
        self.run_cmd_and_update_state(
            cmd,
            puppet_conf,
            "Send CSR Done",
            "Send CSR Error",
            "Failed to send CSR to Puppet Master.",
        )
