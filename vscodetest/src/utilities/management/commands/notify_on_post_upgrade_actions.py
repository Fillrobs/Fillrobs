#!/usr/local/bin/python
from __future__ import unicode_literals

"""
Used by upgrade_cloudbolt.sh to check for items from the upgrade notes that
users might need to do something about after upgrading to a particular version,
and notify admins if there are any such post-upgrade actions necessary.
"""

import sys
from django.core.management.base import BaseCommand

from cbhooks.models import CloudBoltHook, RemoteScriptHook
from common.methods import is_version_newer
from utilities.mail import email_admin


def find_suggested_changes_in_actions_75():
    possible_changes = [
        ("InstallServiceOrderItem", "BlueprintOrderItem"),
        ("installserviceorderitem", "blueprintorderitem"),
        (".isoi", ".boi"),
        ("ServiceOrderItemSerializer", "BlueprintOrderItemSerializer"),
        ("serviceorderitemserializer", "blueprintorderitemserializer"),
        ("InstallServiceItemOptions", "BlueprintItemArguments"),
        ("installserviceitemoptions", "blueprintitemarguments"),
        ("ServiceItemOptionsSerializer", "BlueprintItemArgumentsSerializer"),
        ("serviceitemoptionsserializer", "blueprintitemargumentsserializer"),
        ("service_context", "blueprint_context"),
        ("create_options", "create_arguments"),
        ("create_basic_options", "create_basic_arguments"),
        ("install_service", "deploy_blueprint"),
        ("service-items", "deploy-items"),
        ("sub-service-item", "sub-blueprint-item"),
        ("service-item-options", "blueprint-items-arguments"),
        ("service-item-", "build-item"),
        ("order_service.py", "deploy_blueprint.py"),
    ]

    suggested_changes = ""
    for plugin in CloudBoltHook.objects.all():
        try:
            file_content = plugin.file_content()
        except Exception as err:
            print(
                'Problem getting code for "{}" to check for upgrade '
                "requirements. Exception: {}".format(plugin.name, err)
            )
            continue
        changes_for_action = ""
        for old, new in possible_changes:
            if old in file_content:
                changes_for_action += '\n    Found "{}" that should be changed to "{}"'.format(
                    old, new
                )
        if changes_for_action:
            suggested_changes += '\n\nPlug-in Action "{}":{}'.format(
                plugin.name, changes_for_action
            )
    for script in RemoteScriptHook.objects.all():
        try:
            file_content = script.file_content()
        except Exception as err:
            print(
                'Problem getting code for "{}" to check for upgrade '
                "requirements. Exception: {}".format(script.name, err)
            )
            continue
        changes_for_action = ""
        for old, new in possible_changes:
            if old in file_content:
                changes_for_action += '\n    Found "{}" that should be changed to "{}"'.format(
                    old, new
                )
        if changes_for_action:
            suggested_changes += '\n\nRemote Script Action "{}":{}'.format(
                script.name, changes_for_action
            )

    if suggested_changes:
        suggested_changes = (
            "\n\nChanges to actions needed due to changes to "
            "BP ordering models, methods, contexts & API in "
            "CloudBolt 7.5{}".format(suggested_changes)
        )

    return suggested_changes


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("v1")
        parser.add_argument("v2")

    def handle(self, v1, v2, *args, **options):
        """
        v1 is the version upgrading from, v2 is the version upgrading to
        """
        suggested_changes = find_suggested_changes_in_actions_75()
        if suggested_changes:
            suggested_changes = (
                "Please NOTE: There are some places in your "
                "CloudBolt that should be changed after this "
                "upgrade, per the Upgrade Notes. See below "
                "for details.{}".format(suggested_changes)
            )
            try:
                email_admin(
                    context={
                        "subject": "NOTICE: Post-upgrade changes needed",
                        "message": suggested_changes,
                    }
                )
            except Exception as err:
                print(
                    "Problem sending email to admin about "
                    "upgrade requirements. Exception: {}".format(err)
                )
            # Printing causes it to end up in both the upgrader output and log
            print(suggested_changes)

        message_for_80 = (
            "NOTICE: To support its exciting new features, "
            "CloudBolt 8.0 does include a number of breaking "
            "changes that you may need to take steps to "
            "accommodate. Please review the Upgrade Notes "
            "section of the Release Notes for details."
        )
        # Only print the 8.0 message if they're upgrading from a pre-8.0 version
        if is_version_newer("8.0", v1):
            print(message_for_80)

        sys.exit(0)
