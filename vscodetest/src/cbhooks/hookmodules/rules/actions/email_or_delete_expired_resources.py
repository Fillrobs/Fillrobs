#!/usr/bin/env python

"""
An example action for what can be done with expired resources. Notifies the
resource owner that their resource has expired and checks to see how long the
resource has been expired for. If the resource has been expired for more than a
threshold number of days, a resource deletion job is also created.

Requires a value for the threshold_days_expired input.
"""

import datetime

from common.methods import set_progress, create_delete_jobs_for_resources
from jobs.models import Job
from resources.models import Resource
from utilities.mail import email, InvalidConfigurationException

if __name__ == "__main__":
    import django

    django.setup()

THRESHOLD_DAYS = int("{{threshold_days_expired}}")


def get_days_expired(resource):
    """
    Determines the number of days by which the resource is expired, for use in
    deciding whether to delete it
    """
    exp_date = resource.get_cfv_for_custom_field("expiration_date").value
    now = datetime.datetime.now()
    return (now - exp_date).days


def email_owner(resource, body, subject):
    """
    Send an email to the resource's owner with the given body and subject
    """
    if not resource.owner:
        set_progress(
            "Can't send email for resource {} as it "
            "has no owner.".format(resource.name)
        )
        return

    recipients = [resource.owner.user.email]
    try:
        email_context = {
            "subject": subject,
            "message": body,
        }
        email(recipients=[recipients], context=email_context)
    except InvalidConfigurationException:
        set_progress(
            "Can't send email for resource {} "
            "because can't connect to email "
            "(SMTP) server.".format(resource.name)
        )


def delete_resource_and_send_email(resource, job):
    """
    If the resource is expired enough, create a deletion job for it and send an
    email to inform the owner
    """
    delete_jobs = create_delete_jobs_for_resources([resource], parent_job=job)

    email_body = (
        'This is an email notifying you that your resource "{}" '
        "has been deleted because it was expired by more than "
        "{} days. Please contact your CloudBolt administrator "
        "if you have questions.".format(resource.name, THRESHOLD_DAYS)
    )
    subject = "CloudBolt: Expired resource deletion!"
    email_owner(resource, email_body, subject)

    return Job.wait_for_jobs(delete_jobs)


def send_warning_email(resource, days_expired):
    """
    If the resource is expired but not sufficiently so to merit deleting it,
    simply send a warning email to its owner
    """
    email_body = (
        'This is an email reminder that your resource "{}" '
        "has expired and will be deleted in {} days if no "
        "further action is taken. To prevent this, you can "
        "access the Parameters tab for the resource and "
        "change the value of its Expiration Date.".format(
            resource.name, THRESHOLD_DAYS - days_expired
        )
    )
    subject = "CloudBolt: Resource expiration warning!"
    email_owner(resource, email_body, subject)


def run(job, logger, **kwargs):
    params = job.job_parameters.cast().arguments
    resource_ids = params.get("resource_ids")
    resources = Resource.objects.filter(id__in=resource_ids)
    set_progress("Expiring {} resources.".format(len(resources)))
    results = "", "", ""

    for resource in resources:
        days_expired = get_days_expired(resource)
        msg = "{} expired {} days ago, ".format(resource, days_expired)
        if days_expired >= THRESHOLD_DAYS:
            msg += "deleting it."
            set_progress(msg)
            results = delete_resource_and_send_email(resource, job)
        else:
            msg += "simply sending a warning email."
            set_progress(msg)
            send_warning_email(resource, days_expired)

    return results
