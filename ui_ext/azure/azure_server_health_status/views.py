"""
This plugin pulls data from CloudBolt to show servers for the selected  
Azure Resource Handler 
created on: 2022-01-19 by P Robins
"""
import json
import requests
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from resourcehandlers.azure_arm.models import AzureARMHandler
from resourcehandlers.azure_arm.azure_wrapper import configure_arm_client
from azure.mgmt.resource import ResourceManagementClient
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from extensions.views import report_extension
from infrastructure.models import Environment, Server
from infrastructure.templatetags import infrastructure_tags
from resourcehandlers.models import ResourceHandler
from utilities.permissions import cbadmin_required
from utilities.templatetags import helper_tags
from utilities.logger import ThreadLogger
from django.utils.safestring import mark_safe

from .forms import ResourceHandlerForm

logger = ThreadLogger(__name__)


@report_extension(title="Azure Server Health Status")
def azure_server_health_status(request):

    # Show table
    show_table = False
    resourceHandler = ""

    column_headings = [
        "Asset Name ",
        "Group",
        "Location",
        "Power Status",
    ]
    rows = []

    profile = request.get_user_profile()
    if not profile.super_admin:
        raise PermissionDenied("Only super admins can view this report.")

    if request.method == "GET":
        form = ResourceHandlerForm(initial=dict(resourceHandler=resourceHandler))
    else:

        form = ResourceHandlerForm(request.POST)
        if form.is_valid():

            return_code = ""
            system_status = ""
            show_table = True
            # get the id of the selected resourceHandler
            resourceHandler = form.cleaned_data["resourceHandler"]
            rh = ResourceHandler.objects.filter(id=resourceHandler).first()

            #  GET Azure Connections
            for handler in AzureARMHandler.objects.all():
                wrapper = handler.get_api_wrapper()
                web_client = configure_arm_client(wrapper, WebSiteManagementClient)
                resource_client = wrapper.resource_client
                compute_client = wrapper.compute_client

            targetGroup = "MetsiAzureRG"
            # group_list = resource_client.resource_groups.list(name=targetGroup)
            group_list = resource_client.resource_groups.list()
            for g in list(group_list):
                # print(g.id + " " + g.name + " " + g.location)
                gname = g.name
                # if gname == targetGroup:
                resource_list = resource_client.resources.list_by_resource_group(
                    gname, expand="created: Time,changedTime"
                )
                for resource in list(resource_list):
                    # print(f"{resource.name}")
                    vmname = resource.name
                    """
                    example
                    {'additional_properties': {'changedTime': '2022-01-25T02:19:13.0669755Z',
                    'createdTime': '2022-01-25T02:06:57.3815076Z'},
                    'id': '/subscriptions/ea8bcb02-3d97-4eeb-ad2e-87e6238c8768/resourceGroups/MetsiAzureRG/providers/Microsoft.Compute/virtualMachines/PRWIN201901',
                    'name': 'PRWIN201901',
                    'type': 'Microsoft.Compute/virtualMachines',
                    'location': 'ukwest',
                    'tags': None, 'plan': None, 'properties': None, 'kind': None, 'managed_by': None, 'sku': None, 'identity': None}

                    """
                    if resource.type == "Microsoft.Compute/virtualMachines":
                        reslocation = resource.location
                        vmdata = compute_client.virtual_machines.instance_view(
                            gname, vmname
                        )
                        vmstatus = vmdata.statuses[
                            len(vmdata.statuses) - 1
                        ].display_status
                        rows.append(
                            (
                                vmname,
                                gname,
                                reslocation,
                                vmstatus,
                            )
                        )
                    reslocation = ""
                    return_code = ""

    return render(
        request,
        "azure_server_health_status/templates/special.html",
        dict(
            show_table=show_table,
            form=form,
            pagetitle="Azure Server Health Status Report",
            report_slug="Azure Server Health Status Table",
            intro="""
            Azure Server Health Status Extension.
            """,
            table_caption="Azure Server Health Status Data",
            column_headings=column_headings,
            rows=rows,
        ),
    )
