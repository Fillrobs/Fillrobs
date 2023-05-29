"""
Module contains all views for this extension package.
"""
import requests
from accounts.models import Group, UserProfile
from django.shortcuts import get_object_or_404, render
from extensions.views import dashboard_extension
#from extensions.views import tab_extension, TabExtensionDelegate
# from infrastructure.models import Server
from infrastructure.models import ResourceHandler
from infrastructure.templatetags import infrastructure_tags
from resourcehandlers.vmware.models import VsphereResourceHandler
from resourcehandlers.vmware import pyvmomi_wrapper
from pyVmomi import vmodl, vim
from utilities.templatetags import helper_tags
from utilities.logger import ThreadLogger


logger = ThreadLogger("Datastore Usage report")

def get_obj(content, vim_type, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return [obj]
    else:
        return container.view

def sizeof_fmt(num):
    """
    Returns the human readable version of a file size
    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def get_datastore_info(ds_obj):
    summary = ds_obj.summary
    ds_capacity = summary.capacity
    ds_freespace = summary.freeSpace
    ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    #ds_overp = ds_provisioned - ds_capacity
    #ds_overp_pct = (ds_overp * 100) / ds_capacity if ds_capacity else 0
    
    ds_percent_free = (ds_provisioned/ds_capacity)*100
    ds_data = {
        "Name": ds_obj.name,
        "Capacity":sizeof_fmt(ds_capacity),
        "Used": sizeof_fmt(ds_uncommitted),
        "Freespace":sizeof_fmt(ds_freespace),
        "Percent_Free":str(round(ds_percent_free, 2))
    }

    return ds_data

@dashboard_extension(
    title="Datastore Usage Report", description="This extension shows the Datastore Usage for VMware based ResourceHandlers")
def datastore_usage(request, obj_id=None):
    
    profile = request.get_user_profile()
    is_super_admin = profile.super_admin
    if(is_super_admin == True):
        page_to_show = 'table.html'
    else:
        page_to_show = 'blank.html'     
    rows = []
    column_headings = ['vCenter', 'Datastore', 'Total', 'Used', 'Free', '% Available']
    #column_headings = ['Datastore', 'Total', 'Used', 'Free']
    count_vmware_rh = 0
    # rather than server - we'll get all ResourceHandlers of VMware type
    #server = Server.objects.get(id=server_id)
    vmware_rh = ResourceHandler.objects.filter(resource_technology_id=1)
    count_vmware_rh = vmware_rh.count()

    # get execution history for scheduled tasks
    gethistory = False
    
    #rh = server.resource_handler.cast()


    for rh in vmware_rh:
        wrapper = rh.get_api_wrapper()
        si = wrapper._get_connection()
        datastores = []
        vcentername = rh.name
        content = si.RetrieveContent()
        # Search for all ESXi hosts
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.Datastore],
                                                            True)
        for v in objview.view:                                                        
            datastores.append(get_datastore_info(v))


        # logger.info(f"datastores = {datastores}")
        datastore_rows = []
        for d in datastores:
            datastore_rows.append(
                "<td>"
                + vcentername 
                + "</td><td>"
                + d['Name']
                + "</td><td>"
                + d['Capacity']
                + "</td><td>"
                + d['Used']
                + "</td><td>"
                + d['Freespace']
                + "</td><td>"
                + d['Percent_Free']
                + "</td>",
            )
            
        #logger.info(f"datastore_rows = {datastore_rows}")


    return render(
                request,
                f"datastore_usage/templates/{page_to_show}",
                dict(
                    pagetitle="Datastore Usage REPORT",
                    report_slug="Datastore-Usage-Table",
                    intro="""
                    Datastore Usage extension.
                    """,
                    column_headings=column_headings,
                    rows=datastore_rows,
                ),
            )
