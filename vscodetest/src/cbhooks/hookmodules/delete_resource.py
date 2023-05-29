#!/usr/local/bin/python
from bs4 import BeautifulSoup
from collections import defaultdict

from cbhooks import run_hooks
from cbhooks.exceptions import TerraformActionException
from cbhooks.models import ResourceAction
from cbhooks.services import TerraformService
from common.methods import (
    set_progress,
    create_decom_job_for_servers,
    settings,
)
from common.views import clear_cached_submenu
from jobs.models import Job
from network_virtualization.nsx_t.models import NSXTLogicalRouterGateway
from resources.models import Resource
from resourcehandlers.vmware.nsx.models import NSXEdge
from utilities.events import add_resource_event
from utilities.exceptions import CloudBoltException
from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


# TODO: This is nsx specific and should be moved to the edge model (#142861383)
def find_interface_index(nsx_api, appliance_identifier, identifier):
    xml = nsx_api.get("api/4.0/edges/{}/vnics".format(appliance_identifier))
    soup = BeautifulSoup(xml, "xml")
    for vnic in soup.findAll("vnic"):
        pg = vnic.find("portgroupId")
        if pg and pg.contents[0] == identifier:
            return int(vnic.find("index").contents[0])
    return None


def delete_resource(job, resource):
    result = "", "", ""

    set_progress(
        "Deleting resource ({}) {}".format(resource.resource_type.label, resource.name)
    )

    set_progress("Running global pre-resource delete orchestration actions...")
    run_hooks("pre_delete_resource", job=job, resource=resource)
    resource = Resource.objects.get(id=resource.id)

    set_progress("Running blueprint-specific pre-resource delete actions...")
    pre_status = run_predelete_teardown_sis(job, resource)
    resource = Resource.objects.get(id=resource.id)

    # delete any resources created by Terraform
    terraform_run_context = dict(job=job, resource=resource)
    status, out, err = _purge_terraform_resources(terraform_run_context)
    if status != "SUCCESS":
        return status, out, err

    # Delete all servers
    servers = resource.server_set.exclude(status="HISTORICAL")
    if servers.exists():
        set_progress("Creating sub-job(s) to delete servers")
        child_jobs = create_decom_job_for_servers(
            servers, owner=job.owner, parent_job=job
        )
        result = Job.wait_for_jobs(child_jobs)

    # Load balancer
    for load_balancer in resource.loadbalancer_set.all():
        load_balancer.cast().destroy()
        set_progress('Load balancer "{}" deleted.'.format(load_balancer.name))

    # Networks
    for network in resource.softwaredefinednetwork_set.all():
        resource_handler = network.resource_handler.cast()
        if resource_handler.sdn_mapping.count() > 0:
            # remove it from the tier1 gateway
            gateway = NSXTLogicalRouterGateway.objects.filter(
                uuid=network.appliance_identifier
            ).first()
            gateway.detach_segment(network)
        else:
            nsx_api = resource_handler.nsx_endpoint_api_wrapper()
            idx = find_interface_index(
                nsx_api, network.appliance_identifier, network.identifier
            )
            if not idx:
                return (
                    "FAILURE",
                    "",
                    "Could not determine vnic index for software-defined network {}".format(
                        network
                    ),
                )
            set_progress("Deleting vnic {} at index {}".format(network.identifier, idx))
            nsx_api.request(
                "DELETE",
                "api/4.0/edges/{}/vnics/{}".format(network.appliance_identifier, idx),
            )
        resource_handler.delete_advanced_network(network)

    # NSX Edge Gateways, if applicable
    # By default, these will not be deleted. Create a delete_edge parameter and
    # add it to the resource to enable Edge Gateway deletion.
    if hasattr(resource, "delete_edge") and resource.delete_edge:
        for appliance in resource.softwaredefinednetworkappliance_set.all():
            edge = NSXEdge.objects.filter(object_id=appliance.identifier).first()
            if edge:
                nsx_api = edge.vcenter.nsx_endpoint_api_wrapper()
                nsx_api.request(
                    "DELETE", "api/4.0/edges/{}".format(appliance.identifier)
                )
                edge.delete()

    # release any RPVS being consumed by this Resource
    for rpvs in resource.resourcepoolvalueset_set.all():
        rpvs.resource = None
        rpvs.save()

    # delete any sub-components (sub-resources)
    sub_components = resource.sub_components.exclude(lifecycle="HISTORICAL")
    if sub_components:
        action = ResourceAction.objects.get(label="Delete")
        child_jobs = []
        for sub_component in sub_components:
            # Use the override_requires_approval flag to always create a sub-Job, even if the "Delete"
            # Resource Action is set to require approval. This is safe because the deletion of the
            # parent Resource has already been approved by this point.
            child_jobs.extend(
                action.run_hook_as_job(
                    override_requires_approval=True,
                    parent_job=job,
                    resources=[sub_component],
                )
            )
        result = Job.wait_for_jobs(child_jobs)

    # delete any container objects associated with the Resource
    for container_obj in resource.container_objects.exclude(status="HISTORICAL"):
        orchestrator = container_obj.container_orchestrator
        if orchestrator and hasattr(orchestrator, "cast"):
            orchestrator.cast().delete_container_object(container_obj)

    # Mark the resource as historical
    resource.lifecycle = "HISTORICAL"
    resource.save()
    add_resource_event("DECOMMISSION", resource, "Resource was deleted.", job=job)

    # Bust the cached submenu for these users; it will be rendered with
    # correct list of resources the next time a page is requested.
    if resource.owner:
        clear_cached_submenu(resource.owner.user_id, "resources")
    if job.owner:
        clear_cached_submenu(job.owner.user_id, "resources")

    set_progress("Running blueprint-specific post-resource delete actions...")
    post_status = run_postdelete_teardown_sis(job, resource)
    resource = Resource.objects.get(id=resource.id)

    set_progress("Running global post-resource delete orchestration actions...")
    run_hooks("post_delete_resource", job=job, resource=resource)

    # Return the worst overall status based on teardown SIs and server deletion
    # jobs
    if result[0] == "FAILURE" or pre_status == "FAILURE" or post_status == "FAILURE":
        return "FAILURE", result[1], result[2]
    elif result[0] == "WARNING" or pre_status == "WARNING" or post_status == "WARNING":
        return "WARNING", result[1], result[2]
    return result


def _purge_terraform_resources(terraform_run_context: dict):
    """
    Purge all Terraform-provisioned infra for a given CloudBolt resource.
    """
    status = ("SUCCESS", "All Terraform Resources destroyed successfully.", "")

    from cbhooks.models import TerraformStateFile

    resource = terraform_run_context["resource"]
    group = resource.group
    terraform_run_context["group"] = group

    state_files = TerraformStateFile.objects.filter(resource=resource)

    # Note: This function runs for _all_ `Resources` that are being "deprovisioned".
    # If this `Resource` is _not_ associated with Terraform (e.g. there are no
    # related `TerraformStateFile` objects), exit immediately.
    if not state_files.exists():
        return status

    for state_file in state_files:
        # Need to pass this to our Terraform Destroy command
        state_file_path = state_file.get_abs_file_path()

        # Add the current Terraform State File to the context
        terraform_run_context["state_file_path"] = state_file_path
        terraform_run_context["state_file_obj"] = state_file

        # Get the Terraform environment variables
        tf_env = resource.get_terraform_vars(state_file.id)

        # There were no variables for this state file in the TF_ENV dict
        if tf_env == {}:
            # Check for the old way of storing TF_ENV maps by ServiceItem
            si = state_file.service_item or state_file.config_service_item
            service_item = si.cast()
            tf_env = resource.get_terraform_vars(service_item.id)
            # If both fail this will still be an empty dict which is compatible

        # The hook we are running terraform on
        terraform_plan_action = state_file.hook.cast()

        # The path of that hook's Terraform Plan
        terraform_local_path = terraform_plan_action.local_path

        tf_service = TerraformService(
            local_path=terraform_local_path, hook=terraform_plan_action
        )

        try:
            tf_service.check_enabled_actions("destructive", terraform_run_context)
        except TerraformActionException as e:
            return "FAILURE", "", str(e)

        set_progress(
            "Running Terraform delete actions for "
            f"Terraform Plan '{terraform_local_path}' "
            f"with Terraform State '{state_file_path}'."
        )

        # Ensure the Terraform Plan Dir is initialized
        try:
            tf_service.pre_destroy(tf_env, terraform_run_context, terraform_local_path)
            tf_service.destroy(tf_env, terraform_run_context)
        except TerraformActionException as ex:
            status = (
                "FAILURE",
                "",
                "Command: `{} {} {}` did not exit successfully".format(
                    settings.TERRAFORM_BINARY, ex.action, terraform_local_path
                ),
            )
            tf_service.destroy_failure(terraform_run_context)
            break

    # NOTE: We're using the TerraformService staticmethod (instead of a
    # `tf_service` instance method) because init'ing that class requires a
    # `TerraformPlanHook`, which we don't necessarily have outside of the `for`
    # loop.
    if status[0] == "SUCCESS":
        _ = TerraformService.post_destroy(terraform_run_context)

    _ = TerraformService.destroy_cleanup(terraform_run_context)

    return status


def run_predelete_teardown_sis(decom_job, resource):
    tdsis = [si for si in resource.blueprint.teardown_sis() if si.deploy_seq < 0]
    return run_teardown_sis(resource, decom_job, tdsis)


def run_postdelete_teardown_sis(decom_job, resource):
    tdsis = [si for si in resource.blueprint.teardown_sis() if si.deploy_seq > 0]
    return run_teardown_sis(resource, decom_job, tdsis)


def run_teardown_sis(resource, decom_job, teardown_sis):
    overall_status = ""
    servers = resource.server_set.exclude(status="HISTORICAL")

    child_jobs = []
    for si in teardown_sis:
        set_progress("  Teardown Item: {}".format(si))

        new_child_jobs = si.run_hook_as_job(
            owner=decom_job.owner,
            servers=servers,
            resources=[resource],
            parent_job=decom_job,
            context={},
        )
        child_jobs.extend(new_child_jobs)

        if si.execute_in_parallel:
            # Handle next service item immediately
            continue

        jobs_by_status = wait_for_teardown_jobs(child_jobs)

        # at this point we have waited for all the child jobs to complete so we can clear
        # child_jobs for the next iteration of the loop
        child_jobs = []

        if jobs_by_status["FAILURE"]:
            overall_status = "FAILURE"

            # Continue if last service item says 'continue on failure'
            if getattr(si, "continue_on_failure", False):
                # mark the parent job as a failure, but keep going
                set_progress('  Action failed but has "Continue on Failure" set.')
                continue
            else:
                raise CloudBoltException(
                    "Resource ({}) deletion failed".format(resource.resource_type.label)
                )
        elif jobs_by_status["WARNING"]:
            overall_status = "WARNING"

    return overall_status


def wait_for_teardown_jobs(child_jobs):
    jobs_by_status = defaultdict(list)
    for job in child_jobs:
        job = job.wait_for_completion()
        set_progress("{} {}".format(job, job.status_display()))
        jobs_by_status[job.status].append(job)
    return jobs_by_status


def run(job, **kwargs):
    params = job.job_parameters.cast()
    resources = params.resources.all()
    final_results = ("SUCCESS", "", "")
    for resource in resources:
        results = delete_resource(job, resource)
        if results[0] not in ["SUCCESS", ""]:
            final_results = results

    return final_results
