import time
import os
import json


from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.html import format_html

from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from common.methods import columnify
from extensions.views import dashboard_extension

from utilities.decorators import dialog_view
from resourcehandlers.aws.models import AWSHandler
from extensions.views import report_extension
from utilities.templatetags.helper_tags import render_simple_link

from extensions.views import admin_extension, tab_extension, TabExtensionDelegate
from infrastructure.models import CustomField, Environment
from resourcehandlers.models import ResourceHandler
from resourcehandlers.aws.models import AWSHandler
from utilities.permissions import cbadmin_required
import boto3 
from botocore.exceptions import ClientError
from utilities.logger import ThreadLogger

from .forms import (AWSCreateNewSgForm,
                    AWSDeleteSgForm,
                    AWSCreateSgInboundForm,
                    AWSDeleteSgInboundForm,
                    AWSCreateSgOutboundForm,
                    AWSDeleteSgOutboundForm,
                    AWSCreateSgTagForm,
                    AWSDeleteSgTagForm,
                    )

logger = ThreadLogger(__name__)

def get_aws_data(env_id, aws_sg_id):
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    ec2_client = boto3.client('ec2',
                              region_name=region,
                              aws_access_key_id=rh.serviceaccount,
                              aws_secret_access_key=rh.servicepasswd
                              )    
    ec2secgr = ec2_client.describe_security_groups()
    cnt = 1
    data = []
    group_id = ''
    ipProtocol = ''
    group_name = ''
    group_desc = ''
    vpcid = ''
    # logger.info("ec2secgr=" + str(ec2secgr))
    for e in ec2secgr["SecurityGroups"]:
        # logger.info("cnt = " + str(cnt) + " aws_sg_id = " + str(aws_sg_id))
        if str(cnt) == str(aws_sg_id):
            group_id = e["GroupId"]
            # logger.info("group_id=" + str(group_id))
            group_name = e["GroupName"]
            group_desc = e["Description"]
            vpcid = e["VpcId"]
        cnt = cnt + 1 

    data = {
            "group_id": group_id,
            "group_name": group_name,
            "group_desc": group_desc,
            "vpcid": vpcid,
            "region": region
    }
    return data


# aws client
def get_aws_client(resource=None, service_name=None):
    '''
        Gets the client based on the service name and resource passed
    '''
    rh = AWSHandler.objects.get(id=resource.rh_id)

    client = rh.get_boto3_client(
        service_name=service_name,
        region_name=resource.s3_bucket_region
    )
    return client


def resolve_ipProtocol(ipProtocol):
    if ipProtocol == -1:
        ipProtocol = 0
    if ipProtocol == 1:
        ipProtocol = 'tcp'
    elif ipProtocol == 2:
        ipProtocol = 'udp'
    elif ipProtocol == 3:
        ipProtocol = 'icmp'
    elif ipProtocol == '0':
        ipProtocol = -1
    elif ipProtocol == 'tcp':
        ipProtocol = 1
    elif ipProtocol == 'udp':
        ipProtocol = 2
    elif ipProtocol == 'cmp':
        ipProtocol = 3
    else:
        ipProtocol = 'Unknown'

    return ipProtocol


@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def create_new_aws_sg(request, env_id):
    logger.info(f"envid={env_id}")
    env =  Environment.objects.get(id=env_id)
    
    vpcid = env.vpc_id
    region = env.aws_region
    perform_action = 'create_new_aws_sg'
    
    logger.warning(f"edit_aws_sg env_id={env_id}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSCreateNewSgForm(request.POST)
        logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSCreateNewSgForm not valid {form.errors}")
    
    else:
        data = {
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "create_new_aws_sg",
        }    
        form = AWSCreateNewSgForm(initial=data)
              
    
    return {
        "title": "Create New AWS SG",
        "use_ajax": True,
        "action_url": "/create_new_aws_sg/{env_id}/".format(env_id=env_id),
        "form": form,
        "submit": _("Create New SG")
    }     

@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def create_aws_sg_inbound(request, env_id, aws_sg_id):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'create_aws_sg_inbound'
    #logger.info(f"form AWSCreateSgInboundForm = {request.method}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSCreateSgInboundForm(request.POST)
        #logger.info(f"form AWSCreateSgInboundForm valid = {form.is_valid()} {request.POST}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSCreateSgInboundForm not valid {form.errors}")
            
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "create_aws_sg_inbound",
        }    
        form = AWSCreateSgInboundForm(initial=data)
              
    
    return {
        "title": "Create AWS Security Group Inbound Rule",
        "use_ajax": True,
        "action_url": "/create_aws_sg_inbound/{env_id}/{aws_sg_id}/".format(env_id=env_id,aws_sg_id=aws_sg_id),
        "form": form,
        "submit": _("Create")
    } 

# https://pythonguides.com/get-url-parameters-in-django/
@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def delete_aws_sg_inbound(request, env_id, aws_sg_id, igresscnt, ipProtocol, fromPort, toPort):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'delete_aws_sg_inbound'
    logger.info(f"env_id = {env_id} aws_sg_id = {aws_sg_id} igresscnt = {igresscnt} ipProtocol = {ipProtocol} fromPort  = {fromPort} toPort = {toPort} group_id = {group_id} vpcid= {vpcid} region = {region}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSDeleteSgInboundForm(request.POST)
        #logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSDeleteSgInboundForm not valid {form.errors}")
    else:
        data = {
             "group_id": "{group_id}".format(group_id=group_id),
             "igresscnt": "{igresscnt}".format(igresscnt=igresscnt),
             "ipProtocol": "{ipProtocol}".format(ipProtocol=ipProtocol),
             "fromPort": "{fromPort}".format(fromPort=fromPort),
             "toPort": "{toPort}".format(toPort=toPort),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "delete_aws_sg_inbound",
        }    
        #logger.info(f"data= {data}")
        form = AWSDeleteSgInboundForm(initial=data)
              
    
    return {
        "title": "Delete AWS Security Group Inbound Rule",
        "use_ajax": True,
        "action_url": "/delete_aws_sg_inbound/{env_id}/{aws_sg_id}/{igresscnt}/{ipProtocol}/{fromPort}/{toPort}/".format(env_id=env_id,
                                                                      aws_sg_id=aws_sg_id,
                                                                      igresscnt=igresscnt,
                                                                      ipProtocol=ipProtocol,
                                                                      fromPort=fromPort,
                                                                      toPort=toPort),
        "form": form,
        "submit": _("Delete Inbound Rule")
    }
    
    
@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def create_aws_sg_outbound(request, env_id, aws_sg_id):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'create_aws_sg_outbound'
    #logger.info(f"form AWSCreateSgOutboundForm = {request.method}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSCreateSgOutboundForm(request.POST)
        #logger.info(f"form AWSCreateSgOutboundForm valid = {form.is_valid()} {request.POST}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSCreateSgOutboundForm not valid {form.errors}")
            
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "create_aws_sg_outbound",
        }    
        form = AWSCreateSgOutboundForm(initial=data)
              
    
    return {
        "title": "Create AWS Security Group Outbound Rule",
        "use_ajax": True,
        "action_url": "/create_aws_sg_outbound/{env_id}/{aws_sg_id}/".format(env_id=env_id,aws_sg_id=aws_sg_id),
        "form": form,
        "submit": _("Create")
    } 


@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def delete_aws_sg_outbound(request, env_id, aws_sg_id, egresscnt, ipProtocol, fromPort):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'delete_aws_sg_outbound'
    
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSDeleteSgOutboundForm(request.POST)
        #logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSDeleteSgOutboundForm not valid {form.errors}")
    else:
        data = {
             "group_id": "{group_id}".format(group_id=group_id),
             "egresscnt": "{egresscnt}".format(egresscnt=egresscnt),
             "ipProtocol": "{ipProtocol}".format(ipProtocol=ipProtocol),
             "fromPort": "{fromPort}".format(fromPort=fromPort),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "delete_aws_sg_outbound",
        }    
        form = AWSDeleteSgOutboundForm(initial=data)
              
    
    return {
        "title": "Delete AWS Security Group Outbound Rule",
        "use_ajax": True,
        "action_url": "/delete_aws_sg_outbound/{env_id}/{aws_sg_id}/{egresscnt}/{ipProtocol}/{fromPort}/".format(env_id=env_id,
                                                                          aws_sg_id=aws_sg_id,
                                                                          egresscnt=egresscnt,
                                                                          ipProtocol=ipProtocol,
                                                                          fromPort=fromPort,
                                                                          ),
        "form": form,
        "submit": _("Delete Outbound Rule")
    }

@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def delete_aws_sg(request, env_id, aws_sg_id):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'delete'
    
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSDeleteSgForm(request.POST)
        #logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSSgForm not valid {form.errors}")
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "delete",
        }    
        form = AWSDeleteSgForm(initial=data)
              
    
    return {
        "title": "Delete AWS Security Group",
        "use_ajax": True,
        "action_url": "/delete_aws_sg/{env_id}/{aws_sg_id}/".format(env_id=env_id,aws_sg_id=aws_sg_id),
        "form": form,
        "submit": _("Delete")
    }     

@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def create_aws_sg_tag(request, env_id, aws_sg_id):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'create_aws_sg_tag'
    #logger.info(f"form CreateSgTag = {request.method}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSCreateSgTagForm(request.POST)
        logger.info(f"form del valid = {form.is_valid()} {request.POST}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSCreateSgTagForm not valid {form.errors}")
            
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "create_aws_sg_tag",
        }    
        form = AWSCreateSgTagForm(initial=data)
              
    
    return {
        "title": "Create AWS Security Group Tag",
        "use_ajax": True,
        "action_url": "/create_aws_sg_tag/{env_id}/{aws_sg_id}/".format(env_id=env_id,aws_sg_id=aws_sg_id),
        "form": form,
        "submit": _("Create")
    } 


@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def delete_aws_sg_tag(request, env_id, aws_sg_id, tag_key):
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'delete_aws_sg_tag'
    
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSDeleteSgTagForm(request.POST)
        #logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            logger.info(f"AWSSgForm not valid {form.errors}")
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "tag_key": "{tag_key}".format(tag_key=tag_key),
             "perform_action": "delete_aws_sg_tag",
        }    
        form = AWSDeleteSgTagForm(initial=data)
              
    
    return {
        "title": "Delete AWS Security Group Tag",
        "use_ajax": True,
        "action_url": "/delete_aws_sg_tag/{env_id}/{aws_sg_id}/{tag_key}/".format(env_id=env_id,aws_sg_id=aws_sg_id,tag_key=tag_key),
        "form": form,
        "submit": _("Delete Tag")
    }

    
@dialog_view(template_name='aws_sg_edit/templates/modal.html')
def edit_aws_sg(request, env_id, aws_sg_id):
    # unused - noe edit available yet for modifying the group name or desc - have to delete and re-add
    data = get_aws_data(env_id, aws_sg_id)   
    group_id = data["group_id"]
    group_name = data["group_name"]
    group_desc = data["group_desc"]
    vpcid = data["vpcid"]
    region = data["region"]
    perform_action = 'edit'
    
    #logger.warning(f"edit_aws_sg env_id={env_id} aws_sg_id = {aws_sg_id}")
    if request.method == 'POST':
        profile = request.get_user_profile()
        form = AWSSgForm(request.POST)
        #logger.info(f"form valid = {form.is_valid()}")
        if form.is_valid():
            success, msg = form.save()
            #logger.info(f"success={success}")
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
            #return HttpResponseRedirect(reverse("edit_aws_sg", args=[env.id,aws_sg_id]))
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
    else:
        data = {
             "aws_sg_id": "{aws_sg_id}".format(aws_sg_id=aws_sg_id),
             "group_id": "{group_id}".format(group_id=group_id),
             "group_name": "{group_name}".format(group_name=group_name),
             "group_desc": "{group_desc}".format(group_desc=group_desc),
             "vpcid": "{vpcid}".format(vpcid=vpcid),
             "region": "{region}".format(region=region),
             "env_id": "{env_id}".format(env_id=env_id),
             "perform_action": "edit",
        }    
        form = AWSSgForm(initial=data)
              
    
    return {
        "title": "Edit AWS SG",
        "use_ajax": True,
        "action_url": "/edit_aws_sg/{env_id}/{aws_sg_id}/".format(env_id=env_id,aws_sg_id=aws_sg_id),
        "form": form,
        "submit": _("Save")
    }     
 



class AWSSecurityGroupDelegate(TabExtensionDelegate):
    def should_display(self, **kwargs):
        # Only display for AWS
        env = self.instance
        if env.resource_handler.cast().type_slug != "aws":
            return False
        return True
    
#@report_extension
@tab_extension(model=Environment, title='AWS Security Group Editor', description='Used to edit AWS Security Group data',delegate=AWSSecurityGroupDelegate)
def aws_sg_edit(request, obj_id):
    """
    View for managing the AWS Security Groups
    """

    profile = request.get_user_profile()
    env = Environment.objects.get(id=obj_id)

    rh = env.resource_handler.cast()
    region = env.aws_region
    ec2_client = boto3.client('ec2',
                              region_name=region,
                              aws_access_key_id=rh.serviceaccount,
                              aws_secret_access_key=rh.servicepasswd
                              )
    column_headings = [
        "#",
        "Security Group ID",
        "AWS Group Name",
        "Description",
        "VPCID",
        "Modify"  
        ]

    rows = []
    igressRules = []
    egressRules = []
    sgTags = []
    ec2secgr = ec2_client.describe_security_groups()
    igressmodifylink = ''
    egressmodifylink = ''
    cntb = 1
    
    cnt = 1
    igressrulecnt = 0
    egressrulecnt = 0
    for e in ec2secgr["SecurityGroups"]:
        linkhtml = "<button id=\"getData\" class=\"btn btn-primary\">Select</button>&nbsp;"
        #linkhtml = linkhtml + "<a href=\"/edit_aws_sg/" + str(env.id) + "/" +  str(cnt) + "/\" class=\"btn btn-default open-dialog\">Edit</a>"
        linkhtml = linkhtml + "<a href=\"/delete_aws_sg/" + str(env.id) + "/" +  str(cnt) + "/\" class=\"btn btn-danger open-dialog\">Delete</a>"  
        group_id = e["GroupId"]
        rows.append(
                        (
                            cnt,
                            e["GroupId"],
                            e["GroupName"],
                            e["Description"],
                            e["VpcId"],
                            linkhtml
                        )
        )
          
        if(len(e["IpPermissions"]) > 1):
            for i in e["IpPermissions"]:
                igressrulecnt = igressrulecnt + 1
                gid = e["GroupId"]
              
                if "FromPort" not in i:
                    ipP = resolve_ipProtocol(i["IpProtocol"])
                    
                    frP = "NULL"
                    toP = "NULL"
                    igressmodifylink = "<a href=\"/delete_aws_sg_inbound/" + str(env.id) + "/" + str(cnt) + "/" + str(igressrulecnt) + "/" + str(ipP) + "/" + str(frP) + "/" + str(toP) + "/\" class=\"btn btn-danger open-dialog\">Delete</a>" 
                    igressRules.append(
                        (
                          cnt,
                          igressrulecnt,
                          e["GroupId"], 
                          "NULL",
                          i["IpProtocol"], 
                          i["IpRanges"], 
                          i["Ipv6Ranges"],
                          i["PrefixListIds"],
                          "NULL",
                          igressmodifylink
                        )
                    )     
                else:
                    ipP = resolve_ipProtocol(i["IpProtocol"])
                    frP = i["FromPort"]
                    toP = i["ToPort"]
                    igressmodifylink = "<a href=\"/delete_aws_sg_inbound/" + str(env.id) + "/" + str(cnt) + "/" + str(igressrulecnt) + "/" + str(ipP) + "/" + str(frP) + "/" + str(toP) + "/\" class=\"btn btn-danger open-dialog\">Delete</a>"

                    igressRules.append(
                        (
                          cnt,
                          igressrulecnt,
                          e["GroupId"], 
                          i["FromPort"], 
                          i["IpProtocol"], 
                          i["IpRanges"],
                          i["Ipv6Ranges"],
                          i["PrefixListIds"],
                          i["ToPort"],
                          igressmodifylink
                        )
                    )
                  
        else:
            igressrulecnt = igressrulecnt + 1
            ipP = resolve_ipProtocol(i["IpProtocol"])
            frP = i["FromPort"]
            toP = i["ToPort"]
            igressmodifylink = "<a href=\"/delete_aws_sg_inbound/" + str(env.id) + "/" + str(cnt) + "/" + str(igressrulecnt) + "/" + str(ipP) + "/" + str(frP) + "/" + str(toP) + "/\" class=\"btn btn-danger open-dialog\">Delete</a>"
            igressRules.append(
                         (
                          cnt,
                          igressrulecnt,
                          e["GroupId"], 
                          e["IpPermissions"][0]["FromPort"],
                          e["IpPermissions"][0]["IpProtocol"],
                          e["IpPermissions"][0]["IpRanges"],
                          e["IpPermissions"][0]["Ipv6Ranges"],
                          e["IpPermissions"][0]["PrefixListIds"],
                          e["IpPermissions"][0]["ToPort"],
                          igressmodifylink
                         )
            )  
            
    
        cidr = ''
        if(len(e["IpPermissionsEgress"]) > 1):
            for i in e["IpPermissionsEgress"]:
                egressrulecnt = egressrulecnt + 1
                gid = e["GroupId"]
                ipP = resolve_ipProtocol(i["IpProtocol"])
                if "FromPort" in i:
                    frP = i["FromPort"]
                else:
                    frP = 0
                
                if len(i["IpRanges"]) > 1:
                    for p in i["IpRanges"]:
                        cidr = cidr + p["CidrIp"] + "<br>"
                else:
                    cidr = i["IpRanges"][0]["CidrIp"]
                egressmodifylink = "<a href=\"/delete_aws_sg_outbound/" + str(env.id) + "/" + str(cnt) + "/" + str(egressrulecnt) + "/" + str(ipP) + "/" + str(frP) +  "/\" class=\"btn btn-danger open-dialog\">Delete</a>"    
                egressRules.append(
                        (
                            cntb,
                            egressrulecnt,
                            e["GroupId"],
                            i["IpProtocol"],
                            cidr,
                            frP,
                            i["PrefixListIds"],
                            egressmodifylink
                        )
                )          
        else:
            egressrulecnt = egressrulecnt +1
            if len(i["IpRanges"]) > 1:
                    for p in i["IpRanges"]:
                        cidr = cidr + p["CidrIp"] + "<br>"
            else:
                gid = e["GroupId"]
                if "IpProtocol" not in e:
                    ipP = 0
                else:    
                    if len(e["IpPermissionsEgress"][0]["IpProtocol"]) > 0:
                        ipP = resolve_ipProtocol(e["IpPermissionsEgress"][0]["IpProtocol"])
                    else:
                        ipP = 0
                    
                if "FromPort" not in e:    
                    frP = 0
                else:
                    if len(e["FromPort"]) > 0:
                        frP = e["FromPort"]
                    else:
                        frP = 0    

                egressmodifylink = "<a href=\"/delete_aws_sg_outbound/" + str(env.id) + "/" + str(cnt) + "/" + str(egressrulecnt) + "/" + str(frP) +  "/\" class=\"btn btn-danger open-dialog\">Delete</a>"
                if len(i["IpRanges"]) > 1:
                    cidr = i["IpRanges"][0]["CidrIp"]
                    egressRules.append(
                        (
                        cnt,
                        egressrulecnt,
                        e["GroupId"],
                        e["IpPermissionsEgress"][0]["IpProtocol"],
                        cidr,
                        frP,
                        e["IpPermissionsEgress"][0]["PrefixListIds"],
                        egressmodifylink
                        )
                    )
        cntb = cntb + 1         

        key_to_lookup = "Tags"
        
        
        for tags in ec2secgr["SecurityGroups"]:
            cntc = 1
            if key_to_lookup in tags:
                if tags["GroupId"] == group_id:
                    for t in tags["Tags"]:
                        # del_link points to the Environment, the Group and the tag
                        del_linkhtml = "<a href=\"/delete_aws_sg_tag/" + str(env.id) + "/" +  str(cnt) + "/" + str(cntc) + "/\" class=\"btn btn-danger open-dialog\">Delete</a>"
                        sgTags.append(
                                    (
                                        cnt,
                                        cntc,
                                        group_id,
                                        t['Key'],
                                        t['Value'],
                                        del_linkhtml 
                                    )
                                )    
                        cntc = cntc + 1
        cnt = cnt + 1         
    return render(
        request,
        "aws_sg_edit/templates/aws_sg_edit.html",
        dict(
            pagetitle="AWS Security Group",
            column_headings=column_headings,
            rows=rows,
            env_id=env.id,
            igressRules=igressRules,
            egressRules=egressRules,
            sgTags=sgTags
        ),
    )
