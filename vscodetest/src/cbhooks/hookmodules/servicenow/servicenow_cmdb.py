from utilities.servicenow_api import ServiceNowAPI


def create_or_update_servicenow_cmdb_record(server, job, *args, **kwargs):
    """
    Create a ServiceNow CMDB Record. Unique server resource id will be sent to ServiceNow.
    Utilize CloudBolt ServiceNowAPI wrapper to make request and process response.
    :param server: A Server instance
    :param job: A Job instance
    """
    service_now_api = ServiceNowAPI()

    # Data to create the CI with
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
        "manufacturer": server.resource_handler.name,
        "short_description": "Updated from CloudBolt job ID {}".format(job.id),
    }

    # Create the CI
    result = service_now_api.create_or_update_ci_record(data)
    if not result:
        job.set_progress(
            "Unable to create or update ServiceNow CI entry for {}.".format(
                server.hostname
            )
        )
        return "FAILURE", "", ""

    job.set_progress(f"Updated ServiceNow CMDB for {server.hostname}")
    return "SUCCESS", "", ""


def delete_servicenow_cmdb_record(server, job, *args, **kwargs):
    """
    Delete a ServiceNow CMDB Record if one exists.
    Will search ServiceNow for unique server resource id and delete entry.
    Utilize CloudBolt ServiceNowAPI wrapper to make request and process response.
    :param server: A Server instance
    :param job: A Job instance
    """
    service_now_api = ServiceNowAPI()

    # Delete the CI
    result = service_now_api.delete_ci_record(server)
    if not result:
        job.set_progress(
            "Unable to remove {} from ServiceNow CMDB table.".format(server.hostname)
        )
        return "FAILURE", "", ""

    return "SUCCESS", "", ""
