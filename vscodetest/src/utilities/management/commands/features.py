#!/usr/local/bin/python

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Commands for manipulating CloudBolt features."

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help=(
                "Reset features to those declard in Settings or overridden in Custom Settings. "
                "!! Deletes all features not declared in a `settings.py` file !! "
                "Override features in Customer Settings like so: "
                '`FEATURE_REGISTRY["namespace::feature"] = True|False`'
            ),
        )
        parser.add_argument(
            "-e",
            "--enable",
            metavar="FEATURE_NAME",
            default=None,
            help=("Enable a Feature in CloudBolt."),
            type=str,
        )
        parser.add_argument(
            "-d",
            "--disable",
            metavar="FEATURE_NAME",
            default=None,
            help=("Disable a Feature in CloudBolt."),
            type=str,
        )
        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help=("List features enabled in the CloudBolt Feature Registry."),
        )

    def action_reset(self):
        from features.methods import reload_features

        reload_features(clean=True)

        print("Success!")

    def action_enable(self, feature_name: str):
        from features.methods import get_feature

        f = get_feature(feature_name)

        if f:
            f.enable()
            self.print_feature(f)
        else:
            print(
                (
                    "Could not find feature with name `{name}`.\n"
                    "Run `manage.py features --list` to see all avaliable features."
                ).format(name=feature_name)
            )

    def action_disable(self, feature_name: str):
        from features.methods import get_feature

        f = get_feature(feature_name)

        if f:
            f.disable()
            self.print_feature(f)
        else:
            print(
                (
                    "Could not find feature with name `{name}`.\n"
                    "Run `manage.py features --list` to see all avaliable feature."
                ).format(name=feature_name)
            )

    def print_feature(self, feature) -> None:
        print(
            "{feature} ({active})".format(feature=feature.name, active=feature.active)
        )

    def action_list_features(self):
        from features.methods import get_all_features_q

        print("FEATURE (STATE)")
        for feature in get_all_features_q():
            self.print_feature(feature)

    def handle(self, *args, **options):
        list_features = options.pop("list")
        disable = options.pop("disable")
        enable = options.pop("enable")
        reset = options.pop("reset")

        if list_features:
            self.action_list_features()
        elif disable:
            self.action_disable(disable)
        elif enable:
            self.action_enable(enable)
        elif reset:
            self.action_reset()
