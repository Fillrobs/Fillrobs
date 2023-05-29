from utilities.servicenow_api import ServiceNowAPI


def run(job, logger=None):
    service_now_api = ServiceNowAPI()

    for server in job.server_set.all():
        job.set_progress(
            "Creating new CI in ServiceNow for server {}".format(server.hostname)
        )

        data = {
            "name": server.hostname,
            "company": server.group.name,
            "serial_number": server.resource_handler_svr_id,
            "asset_tag": server.resource_handler_svr_id,
            "operating_system": server.os_build.name,
            "os_version": server.os_build.name,
            "disk_space": server.disk_size,
            "cpu_core_count": server.cpu_cnt,
            "ip_address": server.ip,
            "discovery_source": "Other Automated",
            "manufacturer": server.resource_handler.__str__(),
            "short_description": "Created from CloudBolt job ID {}".format(job.id),
        }

        # create the CI
        result = service_now_api.create_or_update_ci_record(data)

        if not result:
            return "FAILURE", "CI Record not created.", ""

    return "SUCCESS", "", ""
