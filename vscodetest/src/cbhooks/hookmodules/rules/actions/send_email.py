from utilities.mail import email, email_admin


def run(job, logger=None):
    """
    Send an email, given the subject, body, and who to send it to.

    "to" should be a list of email addresses.
    """
    job.set_progress("Preparing to send email.")
    params = job.job_parameters.cast().arguments
    context = params.get("context", {})

    """
    If any legacy params have been provided, add them to the context so
    they will be used by a generic email template
    """
    if params.get("subject"):
        context["subject"] = params.get("subject")
    if params.get("body"):
        context["message"] = params.get("body")

    recipients = params.get("to")
    try:
        if recipients:
            email(slug=params.get("slug"), recipients=recipients, context=context)
        else:
            email_admin(slug=params.get("slug"), context=context)
    except Exception as e:
        job.set_progress("Error sending email: {}".format(e))
        return ("FAILURE", "", "error sending email: {}".format(e))

    return ("", "", "")
