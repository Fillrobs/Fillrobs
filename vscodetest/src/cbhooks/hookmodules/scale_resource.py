#!/usr/local/bin/python

import re

from common.methods import set_progress, create_decom_job_for_servers
from emailtemplates import send_email
from infrastructure.models import Environment
from jobs.models import Job
from orders.models import BlueprintItemArguments, BlueprintOrderItem
from resources.models import Resource
from servicecatalog.models import (
    LoadBalancerServiceItem,
    ServiceItem,
    RunHookServiceItemMixIn,
)
from utilities.events import add_resource_event
from utilities.exceptions import InvalidConfigurationException


def turn_resource_name_into_template(name):
    """
    Check whether a resource name contains integers that may have come from a
    template like 00X, and come up with a version of the name with that template
    in it
    """
    mo = re.search("([0-9]+)", name)
    if mo:
        match = mo.groups()[0]
        name = name.replace(
            match, "".join(["0" for i in range(len(match) - 1)] + ["X"])
        )
    return name


def add_servers(job, resource, pssi, servers_to_add, environment):
    new_bia = get_new_bia(resource, pssi, servers_to_add, environment)

    child_jobs = pssi.start_jobs(new_bia, resource, job)

    # Save the resource on the spawned prov jobs so the new servers will be
    # added to the resource.
    # There is a sliver of a race condition here - it is theoretically possible that the prov job
    # has already started and passed the point at which it would do this.
    for child_job in child_jobs:
        child_job.resource_set.add(resource)
    job.children_jobs.set(child_jobs)

    # Wait for all those job(s) to finish
    results = Job.wait_for_jobs(child_jobs)

    servers = _get_successful_servers_from_jobs(child_jobs)

    if servers:
        # For all new, successfully provisioned servers, run actions that target this tier,
        # then add the new servers to the load balancer
        action_results = run_actions_for_tier(
            resource, pssi, job, new_bia, servers, "UP"
        )
        if action_results[0] != "SUCCESS":
            return action_results
        add_servers_to_lb(resource, pssi, servers)

    return results


def _get_successful_servers_from_jobs(jobs):
    """
    Generate and return a list of all Servers successfully provisioned
    """
    servers = []
    for job in jobs:
        # Refresh the object in memory since it may have changed since originally fetched
        job = Job.objects.get(id=job.id)
        if job.status != "SUCCESS":
            set_progress(
                "Skipping post-actions for any server(s) created by job {} since it did "
                "not succeed".format(job.id)
            )
            continue
        servers.extend(list(job.server_set.all()))
    return servers


def remove_servers(job, resource, pssi, servers_to_remove, environment):
    # Pick the oldest X servers from this tier
    servers_in_tier = resource.server_set.filter(service_item=pssi, status="ACTIVE")
    if environment:
        servers_in_tier = servers_in_tier.filter(environment=environment)
    if not servers_in_tier:
        raise InvalidConfigurationException("No active servers in this tier to remove!")
    if len(servers_in_tier) < servers_to_remove:
        set_progress(
            "Removal of {} severs requested, but only {} active servers found in this "
            "tier. Removing them all.".format(servers_to_remove, len(servers_in_tier))
        )
        servers_to_remove = len(servers_in_tier)

    servers = list(servers_in_tier)[:servers_to_remove]

    server_names_and_ids = [
        "{} (#{})".format(server.hostname, server.id) for server in servers
    ]
    svr_str = ", ".join(server_names_and_ids)
    set_progress(
        "Removing these server(s): {} from tier '{}'".format(svr_str, pssi.name)
    )

    # Remove them from the LB
    for load_balancer in resource.loadbalancer_set.all():
        load_balancer.cast().remove_servers(servers)

    # Run teardown actions that target this tier
    action_results = run_actions_for_tier(resource, pssi, job, None, servers, "DOWN")
    if action_results[0] != "SUCCESS":
        return action_results

    # Delete them
    child_jobs = create_decom_job_for_servers(servers, owner=job.owner, parent_job=job)
    results = Job.wait_for_jobs(child_jobs)
    return results


def get_new_bia(resource, pssi, servers_to_add, environment):
    """
    Return a BlueprintItemArguments instance by duplicating the original or creating a new partial
    instance if the original is not for `environment`.
    """
    # Get the original BIA, so we can duplicate it to recreate the original prov server order(s)
    isj = resource.jobs.first()
    boi = None
    if isj:
        boi = isj.order_item.cast()
    if not isinstance(boi, BlueprintOrderItem):
        # Could enter this case if there's no job or it's not the one that
        # installed the resource
        boi = BlueprintOrderItem.objects.filter(
            resource_name=resource.name, blueprint=resource.blueprint
        ).last()
        # Direct comparison to resource name may not work if a template like 00X
        # was used, so check for that if previous finds nothing
        if not boi:
            templated_resource_name = turn_resource_name_into_template(resource.name)
            boi = BlueprintOrderItem.objects.filter(
                resource_name=templated_resource_name, blueprint=resource.blueprint
            ).last()
    bia = boi.blueprintitemarguments_set.filter(service_item=pssi)
    if environment:
        bia = bia.filter(environment=environment)
    bia = bia.first()
    if bia:
        # Duplicate the original BIA
        # call the duplicate method on the object to preserve m2m relationships
        new_bia = bia.duplicate(boi)
    else:
        # Create a new BIA. This will happen when scaling up a tier to an environment it was
        # not originally deployed to (cloud bursting).
        new_bia = BlueprintItemArguments()
        new_bia.service_item = pssi
        new_bia.environment = environment
        # This is a workaround - the new BIA does not really have an order item or an order,
        # but the BOI is required so we will use the original one that created this tier. This
        # may make the original order look strange and have extra order items.
        new_bia.boi = boi

    new_bia.quantity = servers_to_add
    new_bia.save()
    return new_bia


def run_actions_for_tier(resource, pssi, job, bia, servers, direction="UP"):
    """
    Run any action service items (after new servers have been provisioned for
    the resource or before they are deleted).

    @type resource: resources.models.Resource
    @type servers: list of infrastructure.models.Server
    @return: 3-tuple of status, output, error message
    """
    if direction == "UP":
        service_items = resource.blueprint.deployment_sis()
    else:
        # Run teardown actions for this tier, but only those configured to run *before* the
        # servers are deleted. The others may do damage to the resource, since they're intended to
        # be run when a resource is deleted.
        service_items = resource.blueprint.teardown_sis().filter(deploy_seq__lt=0)

    status = "SUCCESS"
    output_msg = ""

    for si in service_items:
        si = si.cast()
        if not isinstance(si, RunHookServiceItemMixIn):
            # This is not an action, skip
            continue
        if (
            hasattr(si, "targets")
            and si.targets.exists()
            and pssi not in si.targets.all()
        ):
            # This action targets specific tier(s), but not this one
            continue
        if not si.run_on_scale_up and direction == "UP":
            continue
        set_progress("Executing action {}".format(si))

        child_jobs = si.run_hook_as_job(
            owner=job.owner,
            servers=servers,
            resources=[resource],
            parent_job=job,
            context=si.create_hook_context(bia) if bia else {},
        )
        if si.execute_in_parallel:
            continue

        status, output, errors = Job.wait_for_jobs(child_jobs)
        if status and status != "SUCCESS":
            # first check to see if the BP admin has specified that
            # failure is ok for this BP item
            if getattr(si, "continue_on_failure", False):
                # mark the greater `scale resource` job as a failure, but keep going
                status = "FAILURE"
                output_msg = "Resource scaling failed"
                continue

            # stop scaling the resource when one of its jobs fails
            return "FAILURE", "Resource scaling failed", ""
    return status, output_msg, ""


def add_servers_to_lb(resource, pssi, servers):
    # If load balancer(s) exist then add new servers to balancer
    for lb in resource.loadbalancer_set.all():
        set_progress(
            "Checking if servers should be added to Load balancer '{}'".format(lb)
        )
        lbsi = lb.service_item.cast()
        if not isinstance(lbsi, LoadBalancerServiceItem):
            # this is not an LBSI
            continue

        if pssi in lbsi.servers.all():
            lb.add_servers(servers)


def scale_resource(job, resource, pssi, servers_to_add, environment):
    if servers_to_add == 0:
        raise Exception("Servers to add is 0, nothing to do")
    elif servers_to_add < 0:
        return remove_servers(job, resource, pssi, -servers_to_add, environment)
    else:
        return add_servers(job, resource, pssi, servers_to_add, environment)


def run(job, **kwargs):
    params = job.job_parameters.cast()
    args = params.arguments
    environment = None
    if args and "service_item_id" in params.arguments:
        # Check params.arguments (it's running as a rule)
        resource_id = args["resource_id"]
        service_item_id = args["service_item_id"]
        env_id = args.get("environment_id")
        if env_id:
            environment = Environment.objects.get(id=env_id)
        servers_to_add = args["server_count_delta"]
    else:
        # If not, check action inputs (it's running as a resource action)
        service_item_id = "{{ service_item }}"
        servers_to_add = "{{ servers_to_add }}"
        if not service_item_id or "{{ service_item" in service_item_id:
            raise TypeError(
                "Service Item ID parameter is required but was not specified."
            )

    service_item = ServiceItem.objects.get(id=service_item_id).cast()
    if hasattr(params, "resources"):
        # This is true when run as a  resource action
        resources = params.resources.all()
    else:
        resources = [Resource.objects.get(id=int(resource_id))] if resource_id else None
        if not resources:
            raise Exception("No resource provided!")

    final_results = ("SUCCESS", "", "")
    for resource in resources:
        pre_scaling_count = resource.server_count
        results = scale_resource(
            job, resource, service_item, int(servers_to_add), environment
        )
        if results[0] not in ["SUCCESS", ""]:
            # TODO: This makes so only the last failure is returned.  Consider revising to
            # concatenate all failure msgs
            final_results = results
        post_scaling_count = resource.server_count

        set_progress(
            f"pre_scaling_count != post_scaling_count {pre_scaling_count != post_scaling_count}"
        )
        if pre_scaling_count != post_scaling_count:
            # create an event to record  scaling of resource whenever the total of servers changes
            # TODO: Add count delta to message (nice to have)
            add_resource_event("MODIFICATION", resource, "Resource scaled.", job=job)

            recipient = None
            if args and "email_recipient" in params.arguments:
                recipient = args["email_recipient"]

            if recipient:
                set_progress(f"Emailing recipient {recipient}.")
                context = {
                    "message": (
                        f"Auto-scaling rule automatically modified resource server count {resource} from "
                        f"{pre_scaling_count} to {post_scaling_count} based on configured threshold levels."
                    ),
                    "subject": "Auto-scaling rule results",
                }

                send_email(recipients=[recipient], context=context)

    return final_results


def generate_options_for_service_item(resource=None, **kwargs):
    """
    Returns a list of PSSI choices, which are used as options for acting on a
    specific tier of the deployed resource.
    """
    if not resource:
        return []
    blueprint = resource.blueprint
    options = [(pssi.id, pssi.name) for pssi in blueprint.pssis()]
    return options
