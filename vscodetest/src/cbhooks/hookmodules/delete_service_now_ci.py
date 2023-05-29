from utilities.servicenow_api import ServiceNowAPI


def run(job, logger=None):
    service_now_api = ServiceNowAPI()

    for server in job.server_set.all():
        job.set_progress("Removing CI {} from ServiceNow".format(server.hostname))
        result = service_now_api.delete_ci_record(server)

        if not result:
            job.set_progress(
                "Unable to remove {} from ServiceNow".format(server.hostname)
            )

    return "SUCCESS", "", ""
