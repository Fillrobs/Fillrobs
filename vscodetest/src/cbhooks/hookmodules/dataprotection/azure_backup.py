from dataprotection.models import DataProtection, ProtectionPlan
from infrastructure.models import Server, Job


def add_server_to_dataprotection_plan(
    job: Job,
    server: Server,
    dataprotection_instance: DataProtection,
    protection_plan_instance: ProtectionPlan,
) -> bool:
    """
    Add the provided server to a protection plan provided by the
    data protection backend. This triggers the backend to start
    backing up the server according to the parameters of the plan.
    """
    so = dataprotection_instance.cast().get_service_object()
    job.set_progress(
        f'Refreshing "{dataprotection_instance.name}" data protection index'
    )
    # Refresh the backend so it can find the new VM
    so.refresh_backend(server)
    # Use the service object to add the server to the protection plan
    job.set_progress(
        f'Adding {server.hostname} to data protection plan: "{protection_plan_instance.specifier}"'
    )
    so.add_to_protection_plan([server], protection_plan_instance)
    return True


def remove_server_from_dataprotection_plan(
    server: Server,
    dataprotection_instance: DataProtection,
    protection_plan_instance: ProtectionPlan,
) -> bool:
    """
    Remove the provided server from a protection plan provided by the
    data protection backend.
    """
    so = dataprotection_instance.cast().get_service_object()
    try:
        so.remove_from_protection_plan([server], protection_plan_instance)
    except AssertionError:
        # VM may have been removed from the protection plan in Azure
        return False
    return True
