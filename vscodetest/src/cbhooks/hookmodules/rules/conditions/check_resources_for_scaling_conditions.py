import json

from cbhooks.models import CloudBoltHook
from common.methods import set_progress
from emailtemplates import send_email  # noqa: F401
from infrastructure.models import Environment
from resources.models import Resource
from utilities.exceptions import NotFoundException
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def get_cpu_usage(resource, tier_id_or_name, servers, environment):
    if not servers:
        # no servers in the tier currently, consider this no utilization
        return 0
    resource_technology = environment.resource_handler.resource_technology

    if resource.simulated_cpu_load:
        set_progress(
            "Found simulated_cpu_load parameter on the resource. Will use that instead of "
            "determining the actual load."
        )
        # Note that, in this situation, this hook is used regardless of env/group/tech restrictions
        hooks = CloudBoltHook.objects.filter(name="Get CPU Utilization from Parameter")
    else:
        hooks = CloudBoltHook.objects.filter(name__startswith="Get CPU Utilization")
        hooks = hooks.filter(groups=resource.group) | hooks.filter(groups=None)
        hooks = hooks.filter(environments=environment) | hooks.filter(environments=None)
        hooks = hooks.filter(resource_technologies=resource_technology) | hooks.filter(
            resource_technologies=None
        )
    if not hooks.exists():
        set_progress(
            "    No CloudBolt Plug-in found to determine CPU utilization for tier {}".format(
                tier_id_or_name
            )
        )
        return None
    if hooks.count() > 1:
        set_progress(
            "    More than one CloudBolt Plug-in found to determine CPU utilization for tier {}: {},"
            " using the first one".format(tier_id_or_name, hooks)
        )
    hook = hooks.first()
    set_progress(
        "   Executing CloudBolt Plug-in {} to determine CPU usage".format(hook)
    )
    module = hook.get_runtime_module()
    # TODO: verify the get_cpu_utilization() method returned an integer or None
    return module.get_cpu_utilization(servers)


def get_tier_id_from_name(resource, tier_id_or_name):
    """
    :param resource: a Resource object
    :param tier_id_or_name: an ID or name of a tier (PSSI) within that resource
    :return: the ID of the tier
    :raises a NotFoundException if it doesn't exist.
    """
    try:
        return int(tier_id_or_name)
    except ValueError:
        # it must be the name, a string
        pass
    service_item = resource.blueprint.serviceitem_set.filter(name=tier_id_or_name)
    if not service_item:
        raise NotFoundException(
            "No build item found with name or ID matching '{}' on resource {}.".format(
                tier_id_or_name, resource
            )
        )
    return service_item.first().id


def _scale_up_to_min_servers(resource, env, tier_id, tier_config, current_server_count):
    """
    Check whether the tier is below the min # of servers.

    :return: dictionary specifying how to scale this tier (empty if above/at the min)
    """
    min_servers = tier_config.get("min_servers")
    if not min_servers or current_server_count >= min_servers:
        return {}

    delta = min_servers - current_server_count
    set_progress(
        "    Tier has less than the minimum number of servers ({}) in {}, "
        "scaling this tier up by {} server(s)".format(min_servers, env, delta)
    )
    return {
        "server_count_delta": delta,
        "resource_id": resource.id,
        "service_item_id": tier_id,
    }


def _scale_down_to_max_servers(
    resource, env, tier_id, tier_config, current_server_count
):
    """
    Check whether the tier is above the max # of servers.

    :return: dictionary specifying how to scale this tier (empty if below/at the max)
    """
    max_servers = tier_config.get("max_servers")
    if not max_servers or current_server_count <= max_servers:
        return {}

    delta = current_server_count - max_servers
    set_progress(
        "    Tier has more than the maximum number of servers ({}) in {}, scaling this "
        "tier down by {} server(s)".format(max_servers, env, delta)
    )
    return {
        "server_count_delta": -delta,
        "resource_id": resource.id,
        "service_item_id": tier_id,
    }


def _scale_up_based_on_load(
    cpu_usage, resource, env, tier_id, tier_config, current_server_count
):
    """
    Check whether the tier is above CPU threshold and should be scaled up.

    :return: dictionary specifying how to scale this tier (empty if it should not be scaled)
    """
    max_cpu_threshold = tier_config.get("cpu_max_threshold", 100)
    if cpu_usage <= max_cpu_threshold:
        set_progress(
            "    CPU usage ({}) is under the max threshold ({})".format(
                cpu_usage, max_cpu_threshold
            )
        )
        return {}

    set_progress(
        "    CPU usage ({}) is over the max threshold ({})".format(
            cpu_usage, max_cpu_threshold
        )
    )
    # Ensure we don't spin up more than the max total servers
    max_servers = tier_config["max_servers"]
    scale_by = tier_config.get("scale_by", 1)
    delta = min(max_servers, current_server_count + scale_by) - current_server_count
    if delta > 0:
        set_progress("    Scaling this tier up by {} servers in {}".format(delta, env))
        return {
            "server_count_delta": delta,
            "resource_id": resource.id,
            "service_item_id": tier_id,
        }
    burst_env_name = tier_config.get("burst_into")
    if burst_env_name:
        set_progress(
            "    This tier would be scaled up in {}, but it has {} server(s) and is "
            "already at the maximum ({}), so instead it will burst to {}.".format(
                env, current_server_count, max_servers, burst_env_name
            )
        )
        return {"burst_into": burst_env_name}
    set_progress(
        "    This tier would be scaled up in {}, but it has {} server(s) and is already at the "
        "maximum ({})".format(env, current_server_count, max_servers)
    )
    return {}


def _scale_down_based_on_load(
    cpu_usage, resource, env, tier_id, tier_config, current_server_count
):
    """
    Check whether the tier is below CPU threshold and should be scaled down.

    :return: dictionary specifying how to scale this tier (empty if it should not be scaled)
    """
    min_cpu_threshold = tier_config.get("cpu_min_threshold", 0)
    if cpu_usage >= min_cpu_threshold:
        set_progress(
            "    CPU usage ({}) is over the min threshold ({})".format(
                cpu_usage, min_cpu_threshold
            )
        )
        return {}

    logger.debug(
        "    CPU usage ({}) is under the min threshold ({})".format(
            cpu_usage, min_cpu_threshold
        )
    )
    scale_by = tier_config.get("scale_by", 1)
    min_servers = tier_config["min_servers"]
    # Ensure we don't spin down to less than the min # of servers
    delta = max(min_servers, current_server_count - scale_by) - current_server_count
    # delta will be negative if the condition is met
    if delta < 0:
        set_progress("    Scaling this tier down by {} server(s)".format(-delta))
        return {
            "server_count_delta": delta,
            "resource_id": resource.id,
            "service_item_id": tier_id,
        }
    set_progress(
        "    This tier would be scaled down, but it has {} server(s) and is already "
        "at the minimum ({})".format(current_server_count, min_servers)
    )
    return {}


def _burst_into_this_environment(resource, tier_id, tier_config, current_server_count):
    """
    Check whether another env for this tier triggered a burst into this env-tier. If so,
    scale up by the number specified in scale_by (or 1 if not defined), limited by the
    max_servers for this env-tier.
    """
    max_servers = tier_config["max_servers"]
    if tier_config.get("burst"):
        scale_by = tier_config.get("scale_by", 1)
        delta = min(max_servers, current_server_count + scale_by) - current_server_count
        return {
            "server_count_delta": delta,
            "resource_id": resource.id,
            "service_item_id": tier_id,
        }
    return {}


def check_tier_scaling_conditions(
    resource, tier_id_or_name, environment_name, tier_config
):
    """
    Check whether the tier is under/over min/max servers, then whether it should be scaled based
    on load.

    :param resource: the deployed Resource object to check
    :param tier_id_or_name: the PSSI to check
    :param tier_config: a dictionary with the scaling thresholds and limits.
    :return: a dictionary specifying how this tier should be scaled. The dict will be empty if
    it is within thresholds.
    """
    tier_id = get_tier_id_from_name(resource, tier_id_or_name)
    env = Environment.objects.get(name=environment_name)
    servers = resource.server_set.filter(
        service_item_id=tier_id, environment=env
    ).exclude(status="HISTORICAL")
    current_server_count = servers.count()

    scaling_needed = (
        _burst_into_this_environment(
            resource, tier_id, tier_config, current_server_count
        )
        or _scale_up_to_min_servers(
            resource, env, tier_id, tier_config, current_server_count
        )
        or _scale_down_to_max_servers(
            resource, env, tier_id, tier_config, current_server_count
        )
    )
    if scaling_needed:
        # If this env-tier is being burst into, or it needs to be brought within the min &
        # max, don't bother checking the CPU, just scale it.
        scaling_needed["environment_id"] = env.id
        return scaling_needed

    cpu_usage = get_cpu_usage(resource, tier_id_or_name, servers, env)
    if cpu_usage is None:
        logger.debug("    No CPU usage gathered")
        return {}

    scaling_needed = _scale_up_based_on_load(
        cpu_usage, resource, env, tier_id, tier_config, current_server_count
    ) or _scale_down_based_on_load(
        cpu_usage, resource, env, tier_id, tier_config, current_server_count
    )
    if scaling_needed:
        scaling_needed["environment_id"] = env.id
        return scaling_needed
    return {}


def get_scaling_config_for_resource(resource):
    """
    :param resource: a Resource object that has `auto_scaling_config` set on it
    :return: the dictionary with the auto-scaling config
    :raise: whatever JSON parsing exception may be raised by json.loads()
    """
    auto_scaling_config = resource.attributes.get(
        field__name="auto_scaling_config"
    ).value
    try:
        auto_scaling_config = json.loads(auto_scaling_config)
    except:  # noqa: E722
        logger.debug(
            "Error parsing auto scaling config: {}".format(auto_scaling_config)
        )
        raise
    logger.debug("Parsed scaling config: {}".format(auto_scaling_config))
    return auto_scaling_config


def check(job, logger):
    """
    Find all resources with an attribute called 'auto_scaling_config', check each tier specified
    in the config for whether it should be scaled up/down.

    :return: a 4-tuple where the last item is a list of dictionaries - each of which specifying
     a tier that should be scaled up or down, and by how much. One scaling action job will be
     spawned for each.
    """
    result_list = []
    # get all the resources with auto scaling config set on them
    resources = Resource.objects.filter(
        attributes__field__name="auto_scaling_config", lifecycle="ACTIVE"
    )
    set_progress(
        "Found {} resources with auto-scaling rules set on them".format(len(resources))
    )
    for resource in resources:
        set_progress("Processing resource {}".format(resource.name))
        scaling_config = get_scaling_config_for_resource(resource)
        logger.debug("  Got scaling config: {}".format(scaling_config))
        for tier_id in list(scaling_config.keys()):
            for environment in list(scaling_config[tier_id].keys()):
                set_progress(
                    "  Processing tier {}, environment {}".format(tier_id, environment)
                )
                result_dict = check_tier_scaling_conditions(
                    resource, tier_id, environment, scaling_config[tier_id][environment]
                )
                burst_env = result_dict.get("burst_into")
                if burst_env:
                    scaling_config[tier_id][burst_env]["burst"] = True
                    # Do not scale the current tier in this case, only burst to another.
                    # This depends on the "burst into" tier coming later than this one.
                    result_dict = {}

                recipient = "{{ email_recipient }}"
                if result_dict:
                    if recipient:
                        result_dict["email_recipient"] = recipient
                    # Aggregate multiple results to cause the Rules engine to run multiple actions
                    result_list.append(result_dict)

    return "SUCCESS", "", "", result_list
