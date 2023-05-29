import os

from django.core.management.base import BaseCommand

from resourcehandlers.vmware.models import VsphereResourceHandler
from utilities.logger import ThreadLogger

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = ThreadLogger(__name__)


def add_uuids_to_vsphere_osbas():
    """
    For each VsphereResourceHandler, set the UUID on any of its VsphereOSBuildAttributes that don't have one.

    It's possible that none of a handlers OSBAs need their UUIDs to be set. In these cases, we don't want to
    unnecessarily call get_all_templates().
    """
    handlers = VsphereResourceHandler.objects.all()
    for handler in handlers:
        vsphere_osbas = [osba.cast() for osba in handler.os_build_attributes.all()]
        vsphere_osbas_lacking_uuids = [
            osba for osba in vsphere_osbas if osba.uuid is None
        ]
        if vsphere_osbas_lacking_uuids:
            try:
                handler_templates = handler.get_all_templates()
            except Exception as e:
                logger.warning(
                    "Unable to retrieve templates from {}: {}".format(handler, e)
                )
                continue

            for vsphere_osba in vsphere_osbas_lacking_uuids:
                template_match = next(
                    (
                        template
                        for template in handler_templates
                        if template["name"] == vsphere_osba.template_name
                    ),
                    None,
                )
                if template_match:
                    try:
                        vsphere_osba.uuid = template_match["id"]
                        vsphere_osba.save()
                    except KeyError:
                        logger.info(
                            "UUID unavailable from VMware for template {}, "
                            "in handler {}".format(vsphere_osba.template_name, handler)
                        )
                else:
                    logger.info(
                        "Could not find VMware template: {}.".format(
                            vsphere_osba.template_name
                        )
                    )


class Command(BaseCommand):
    help = "Set the UUID for any VMware templates lacking this attribute."

    def handle(self, *args, **options):
        add_uuids_to_vsphere_osbas()
