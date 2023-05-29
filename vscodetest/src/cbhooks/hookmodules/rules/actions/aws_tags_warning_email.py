from django.utils.translation import ugettext as _

from infrastructure.models import Server
from utilities.mail import email


def run(job, logger=None):
    """
    Given a list of AWS servers missing required tags, send an email to their
    owners
    """
    job.set_progress("Preparing to send AWS missing tags warning emails.")
    params = job.job_parameters.cast().arguments
    for violator in params["violators"]:
        server_id = violator["server"]
        server = Server.objects.filter(id=server_id).first()
        missing_tags = violator["missing_tags"]
        owner = [server.owner.user.email]
        email_context = {"server": server, "missing_tags": missing_tags}

        if owner is None:
            job.set_progress(_("No recipients specified"))
            return ("", "", "")

        try:
            email(recipients=owner, slug="aws-missing-tags", context=email_context)
        except Exception as e:
            return ("FAILURE", "", "error sending email: {}".format(e))

    return ("", "", "")
