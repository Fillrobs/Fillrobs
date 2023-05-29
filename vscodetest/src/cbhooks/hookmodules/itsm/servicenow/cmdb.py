from infrastructure.models import Server
from jobs.models import Job
from itsm.models import ITSM, CMDB


def create_or_update_servicenow_cmdb_record(server: Server, job: Job, *args, **kwargs):
    """
    Create a ServiceNow CMDB Record. Unique server resource ID will be sent to ServiceNow.
    Utilize CloudBolt ServiceNowWrapper wrapper to make request and process response.
    :param server: The Server instance to create or update a CI record for.
    :param job: The Job which this will run in.
    :param kwargs['cmdb_id'] The CMDB id which can be used to customize payload sent to ServiceNow.
    """

    try:
        cmdb_id = kwargs.pop("cmdb_id")
    except KeyError:
        error = "CMDB ID not found. The ServiceNow cmdb hook is enabled but no CMDB data set was found. Completing job with a success."
        return "SUCCESS", "", error

    """
    Establish ITSM and CMDB objects in order to utilize context and payload
    """
    try:
        cmdb = CMDB.objects.get(pk=cmdb_id)
        itsm = ITSM.objects.get(pk=cmdb.itsm.id)
        context = cmdb.get_context(server=server, job=job)
    except Exception as error:
        return "FAILURE", "", error

    """
    If server is being deleted (marked as "HISTORICAL"), we'll sent a limited payload to ServiceNow.
    name, discovery_source, install_status are required.
    The default HISTORICAL install_status for ServiceNow is 7. You can change this in your cmdb data config.
    """
    if server.status == "HISTORICAL":
        data_context = cmdb.get_context_data(context)
        data = {
            "name": data_context["name"],
            "discovery_source": data_context["discovery_source"],
            "install_status": data_context["install_status"],
        }
    else:
        data = cmdb.get_context_data(context)

    """
    data is now a dictionary of key:value pairs which will be converted to json and sent to api/now/identifyreconcile endpoint of your ServiceNow service.
    The payload resembles the following sample:
    {
        "items":
        [
            {
                "className": "cmdb_ci_server",
                "values": data
            }
        ]
    }
    """

    # Get the appropriate wrapper for this technology.
    service_now_api = itsm.get_api_wrapper()

    # CMDB Table Name (aka className) is configurable. The default is "cmdb_ci_server".
    # This table name can be edited in the cmdb overview configuration page.
    service_now_api.set_cmdb_table_name(cmdb.table_name)

    # Create or update the CI (Configuration Item)
    try:
        result = service_now_api.create_or_update_ci_record(data)
    except RuntimeError as error:
        return "FAILURE", "", error

    if not result:
        job.set_progress(
            "Unable to create or update ServiceNow CI entry for {}.".format(
                server.hostname
            )
        )
        return "FAILURE", "", ""

    job.set_progress(f"Updated ServiceNow CMDB for {server.hostname}")
    return "SUCCESS", "", ""
