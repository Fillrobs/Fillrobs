from __future__ import unicode_literals

all_cfs = [
    {
        "name": "auto_scaling_config",
        "label": "Auto-Scaling Config",
        "type": "CODE",
        "show_on_servers": True,
        "description": (
            "JSON data specifying thresholds and rules for scaling "
            "different tiers of a deployed resource"
        ),
    },
    {
        "name": "simulated_cpu_load",
        "label": "Simulated CPU Load",
        "type": "INT",
        "description": "Test parameter for auto-scaling of deployed resources",
        "show_on_servers": True,
        "required": True,
    },
]

hooks = [
    {
        "name": "Get CPU Utilization for EC2",
        "description": "Used by auto-scaling conditional rule",
        "shared": False,
        "enabled": True,
        "hook_point": None,
        "module": "cbhooks/hookmodules/rules/conditions/get_cpu_utilization_for_ec2_servers.py",
    },
    {
        "name": "Get CPU Utilization for VMware",
        "description": "Used by auto-scaling conditional rule",
        "shared": False,
        "enabled": True,
        "hook_point": None,
        "module": "cbhooks/hookmodules/rules/conditions/get_cpu_utilization_for_vmware_servers.py",
    },
    {
        "name": "Get CPU Utilization from Parameter",
        "description": "Used to test auto-scaling conditional rule",
        "shared": False,
        "enabled": True,
        "hook_point": None,
        "module": "cbhooks/hookmodules/rules/conditions/get_fake_cpu_utilization_from_param.py",
    },
]

# This should have already been created by cb_minimal, but keep the details in
# here to be safe. Should match cb_minimal. Only used in rule below.
scale_action_dict = {
    "name": "Scale Resource",
    "description": (
        "Add or remove servers in a specific tier and update the load "
        "balancer (if one exists)."
    ),
    "shared": True,
    "enabled": True,
    "module": "cbhooks/hookmodules/scale_resource.py",
}

rules = [
    {
        "name": "check_resources_for_scaling_conditions",
        "label": "Check Resources for Scaling Conditions",
        "description": "Auto-scaling support, including cloud bursting between environments, and"
        "alerting a recipient via email when a resource is changed.",
        "condition": {
            "name": "Check Resources for Scaling Conditions",
            "description": "Auto-scaling support, including cloud bursting between environments",
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/check_resources_for_scaling_conditions.py",
            "inputs": [
                {
                    "name": "email_recipient",
                    "label": "Email Recipient",
                    "namespace": "action_inputs",
                    "type": "STR",
                    "required": False,
                }
            ],
        },
        "action": scale_action_dict,
    }
]
