from __future__ import unicode_literals
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
    Retrieve the signed certificate for this PuppetConf from the Puppet Master
    and install it in the appropriate filestore.

    Usage:

        ./manage.py install_puppet_cert puppet_conf_id

    Or run this command from a Django app:

        from django.core import management
        management.call_command('install_puppet_cert', 1)
    """

    def handle(self, *args, **options):
        try:
            conf_id = args[0]
        except IndexError:
            raise RuntimeError("PuppetConf ID not specified")
        puppet_conf = PuppetConf.objects.get(id=int(conf_id))

        certname = puppet_conf.get_cert_name()
        certdir = puppet_conf.get_cert_dir()

        certpath = self.fetch_cert(puppet_conf, certdir, certname)
        self.lockdown_cert(puppet_conf, certpath)

    def fetch_cert(self, puppet_conf, certdir, certname):
        # WHY ARE WE USING CURL?
        # WE HAVE REQUESTS RIGHT?!?
        certpath = "{}/{}.pem".format(certdir, certname)
        cmd = [
            "curl",
            "-k",
            "-H",
            "Accept:s",
            "-o",
            certpath,
            "https://{}:8140/production/certificate/{}".format(
                puppet_conf.hostname, certname
            ),
        ]
        self.run_cmd_and_update_state(
            cmd,
            puppet_conf,
            "Fetch Signed Cert Done",
            "Fetch Signed Cert Error",
            "Failed to fetch SSL certificate from Puppet Master.",
        )
        return certpath

    def lockdown_cert(self, puppet_conf, certpath):
        cmd = ["chmod", "600", certpath]
        self.run_cmd_and_update_state(
            cmd,
            puppet_conf,
            "Install Signed Cert Done",
            "Install Signed Cert Error",
            "Failed to change file permissions of the certificate.",
        )
