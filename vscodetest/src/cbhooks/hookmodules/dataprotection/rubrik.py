import rubrik_cdm
from infrastructure.models import Server, Job
from dataprotection.models import DataProtection, ProtectionPlan


def add_server_to_dataprotection_plan(
    job: Job,
    server: Server,
    dataprotection_instance: DataProtection,
    protection_plan_instance: ProtectionPlan,
) -> bool:
    so = dataprotection_instance.cast().get_service_object()
    job.set_progress(
        'Refreshing "{}" data protection index'.format(dataprotection_instance.name)
    )
    # Refresh the backend so it can find the new VM
    so.refresh_backend(server)
    # Use the service object to add the server to the protection plan
    job.set_progress(
        'Adding {} to data protection plan: "{}"'.format(
            server.hostname, protection_plan_instance.specifier
        )
    )
    so.add_to_protection_plan([server], protection_plan_instance)
    return True


def remove_server_from_dataprotection_plan(
    server: Server,
    dataprotection_instance: DataProtection,
    protection_plan_instance: ProtectionPlan,
) -> bool:
    so = dataprotection_instance.cast().get_service_object()
    try:
        so.remove_from_protection_plan([server], protection_plan_instance)
    except rubrik_cdm.exceptions.InvalidParameterException:
        # VM may have been removed from the protection plan in Rubrik
        return False

    return True
