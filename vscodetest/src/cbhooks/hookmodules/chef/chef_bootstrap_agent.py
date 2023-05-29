"""
This plugin installs the Chef agent on a server during provisioning.
"""

from __future__ import unicode_literals
import os
from utilities.decorators import timeout
from utilities.logger import ThreadLogger
from utilities.run_command import run_command
from utilities.exceptions import CommandExecutionException, NotFoundException
from common.methods import shlex_quote, get_file_for_key_material
from connectors.chef.chefapiwrapper import _add_apps_to_bootstrap_args


logger = ThreadLogger(__name__)
keyfile = None


def generate_options(
    server,
    credentials,
    chefconf,
    chef_environment="",
    knife_bootstrap_additional_args="",
    recipes=[],
    roles=[],
):
    username = credentials.get("username", "root")
    key_name = credentials.get("keyfile")
    key_is_global = credentials.get("key_is_global")
    password = credentials.get("password")

    strip = []

    option_list = []
    option_list.append(server.ip)
    option_list.append("--node-name {}".format(server.hostname))
    option_list.append("--config {}".format(chefconf._knife_config_path))
    option_list.append("--chef-license accept")
    option_list.append("--connection-user {}".format(username))

    if server.is_windows():
        # Use WinRM it this Windows host
        option_list.append("--connection-protocol winrm")
        # this is the port for Remote Management 2.0 over HTTP
        option_list.append("--connection-port 5986")
    else:
        # This is a Linux/Unix host
        option_list.append("--no-host-key-verify")
        if username != "root":
            option_list.append("--sudo")
            option_list.append("--use-sudo-password")

    if key_name:
        # If key-auth is avaliable, use that to SSH to the server instead of a password
        key_location = server.resource_handler
        if key_is_global:
            key_location = "global"
        keyfile = get_file_for_key_material(key_name, key_location=key_location)
        if not keyfile:
            raise NotFoundException(
                "Could not find required key material " "{}".format(key_name)
            )
        option_list.append("--ssh-identity-file {}".format(keyfile))
    elif password:
        # Fall back on password-auth
        escaped_pw = shlex_quote(password)
        option_list.append("--connection-password {}".format(escaped_pw))
        strip.append(escaped_pw)

    if chef_environment is str and len(chef_environment) > 0:
        option_list.append("--environment {}".format(chef_environment))

    # convert the role names to be enclosed in the string "role[]"
    roles = ["role[{}]".format(role) for role in roles]

    apps = recipes + roles

    knife_bootstrap_additional_args = _add_apps_to_bootstrap_args(
        knife_bootstrap_additional_args, apps
    )

    # Add additional bootstrap arguments here
    option_list.append(knife_bootstrap_additional_args)
    options = " ".join(option_list)

    return options, strip


def run(job, server, credentials, chefconf, **kwargs):
    """
    The chefconf object type is ChefAPIWrapper
    """
    chef_environment = kwargs.get("chef_environment", "")
    knife_bootstrap_additional_args = kwargs.get("knife_bootstrap_additional_args", "")
    recipes = kwargs.get("recipes", [])
    roles = kwargs.get("roles", [])
    command = "knife bootstrap"
    options, strip = generate_options(
        server,
        credentials,
        chefconf,
        chef_environment,
        knife_bootstrap_additional_args,
        recipes,
        roles,
    )
    if chefconf._chef_conf.delete_node_if_exists:
        job.set_progress(f"Deleting exising Chef node {server.hostname}")
        chefconf.delete_node_if_exists(server)
    try:
        run_command_with_timeout = timeout(seconds=3600)(run_command)
        run_command_with_timeout(  # noqa: F841
            "{} {}".format(command, options),
            strip,
            # remove all "( %18) ##" progress lines
            # remove all ANSI escape sequences
            output_subs=[
                ("\( *\d+%\)(\x08)*#+", ""),  # noqa: W605
                (r"\033\[\d+m", ""),
            ],
        )
    except CommandExecutionException as err:
        err.output = "Chef agent bootstrap/initial run failed."
        raise err
    except Exception:
        # Just doing try-except so can have finally for temp file deletion,
        # so re-raise
        raise
    finally:
        # delete temporary key file if necessary
        if keyfile:
            os.remove(keyfile)
    return "", "", ""
