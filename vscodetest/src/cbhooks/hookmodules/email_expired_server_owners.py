from collections import defaultdict

from django.template.loader import render_to_string  # noqa: F401

from utilities import mail
from utilities.exceptions import InvalidConfigurationException


def run(job, **kwargs):
    """
    Given a list of servers, send one email per owner to notify
    them.
    """
    status = ""
    errors = ""
    parameters = job.job_parameters.cast()
    # Build a dict mapping owners to a list of their servers
    user_servers = defaultdict(list)
    for server in parameters.servers.all():
        user_servers[server.owner].append(server)

    for owner, servers in list(user_servers.items()):
        recipient_email = owner.user.email
        servernames = ", ".join([svr.hostname for svr in servers])
        job.set_progress(
            "Sending email to %s for expiration of servers %s."
            % (recipient_email, servernames)
        )

        email_context = {
            "owner": owner,
            "servers": servers,
        }
        try:
            mail.email(
                recipients=[recipient_email],
                slug="expired-server",
                context=email_context,
            )
        except InvalidConfigurationException as err:
            job.set_progress("WARNING: %s" % err)
            status = "WARNING"
            errors = "%s\n%s" % (errors, err)
    return status, "", errors
