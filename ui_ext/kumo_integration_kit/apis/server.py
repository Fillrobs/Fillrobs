import json
import pprint
import collections
import functools
import operator
import traceback
import time
from datetime import (
    date,
    datetime,
    timedelta
)
from django.http import HttpResponse, JsonResponse

from utilities.decorators import json_view
from infrastructure.models import Server
from resourcehandlers.aws.models import (
    AWSBillingLineItem, 
    AWSHandler, 
    AmazonMachineImage, 
    AwsVpcSubnet, 
    EBSDisk, 
    EC2ServerInfo
)
from xui.kumo_integration_kit.constants import (
    UNUSED_SERVICES,
    UNOPTIMIZED_SERVICES,
    REGIONS_DICT,
)
from xui.kumo_integration_kit.utils import (
    ApiResponse,
    check_for_cache,
    get_cache_data,
    set_cache_data
)


def get_server_data(payload):
    """To get the server data from CB database

    Args:
        payload (dict): payload/params.

    Returns:
        variables: Server's data from database.
    """
    
    volume_list = []
    
    id_list = [payload["instance_id"]]
    volume_id_list = []
    ami_id_list = []
    ip_list = []
    
    s = Server.objects.get(id=payload['server_id'])
    server_provider_type = s.resource_handler.type_slug
    
    if server_provider_type == 'aws':
        provider_account_id = s.resource_handler.cast().account_id
        flavor_id = s.ec2serverinfo.instance_type
        server_region = s.ec2serverinfo.availability_zone
        
        if s.ec2serverinfo.elastic_ip:
            id_list.append(s.ec2serverinfo.elastic_ip)
        
        if server_region[-1].isalpha():
            server_region = server_region[0:-1]
            
        region_name = REGIONS_DICT[server_region]

        # ami_obj = AmazonMachineImage.objects.filter(
        #     resourcehandler=s.resource_handler)
        
        # if list(ami_obj):
        #     for ami in list(ami_obj):
        #         ami_id_list.append(ami.ami_id)
        rh_obj = s.resource_handler.cast()
        aws_data = rh_obj.get_vm_dict(s)
        ami_id_list.append(aws_data['image_id'])
            
        for nic in s.nics.all():
            id_list.append(nic.ip)
            ip_list.append(nic.ip)
            id_list.append(nic.private_ip)
            ip_list.append(nic.private_ip)
        
        for disk in s.disks.all():
            volume_list.append({
                "volume_type": disk.cast().volume_type,
                "volume_size": disk.cast().disk_size
            })
            
            id_list.append(disk.cast().uuid)
            volume_id_list.append(disk.cast().uuid)

        try:
            server_os = s.os_family.name
        except:
            server_os = 'linux'
            
        if s.status == 'ACTIVE':
            status_of_server = 'running'
        else:
            status_of_server = s.status.lower()
            
        return provider_account_id, volume_id_list, ami_id_list, id_list, \
            volume_list, flavor_id, server_os, region_name, server_region, \
            list(set(ip_list)), status_of_server
            
    elif server_provider_type == 'azure_arm':
        provider_account_id = s.resource_handler.cast().serviceaccount
        vm_id = [s.hostname]
        disk_ids = [d.uuid for d in s.disks.all()]
        region_code = s.azurearmserverinfo.location
        resource_group = s.azurearmserverinfo.resource_group 
        ips=[]
        for n in s.nics.all():
            if n.ip:
                ips.append(n.ip)
            if n.additional_ips:
                ips.append(n.additional_ips)
        return provider_account_id, vm_id, disk_ids, region_code, resource_group, ips
    

def get_cost_summary(request):
    """To get the cost summary data

    Args:
        request (get request): get request to get data.

    Returns:
        dict: Server's Cost Summary data.
    """
    
    request_body_dict = {}
    payload = json.loads(request.GET.get('body'))
    if payload['server_provider_type'] == 'aws':
        provider_account_id, volume_id_list, ami_id_list, id_list, \
            volume_list, flavor_id, os_family, region_name, region_code, \
            ip_list, status_of_server = get_server_data(payload=payload)
        
        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['volume_ids'] = volume_id_list
        request_body_dict['instance_id'] = [payload["instance_id"]]
        request_body_dict['amis'] = ami_id_list
        request_body_dict['resource_id'] = list(set(id_list))
        request_body_dict['state'] = status_of_server
        request_body_dict['volumes'] = volume_list
        request_body_dict['flavor_id'] = flavor_id
        request_body_dict['platform'] = os_family
        request_body_dict['region_name'] = region_name
        request_body_dict['region_code'] = region_code

        pprint.pprint(request_body_dict)
    
        response = ApiResponse(
                    request_body_dict, 
                    'get_server_cost_summary').fetch_response()
        
    elif payload['server_provider_type'] == 'azure_arm':
        provider_account_id, vm_id, disk_ids, region_code, \
            resource_group, ips = get_server_data(payload=payload)
        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['vm_id'] = vm_id
        request_body_dict['disk_ids'] = disk_ids
        request_body_dict['region_code'] = region_code
        request_body_dict['resource_group'] = resource_group
        request_body_dict['ips'] = ips
        request_body_dict['mec'] = 'true'

        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                    request_body_dict, 
                    'get_azure_cost_summary').fetch_response()

    if response.status_code == 422:
        return JsonResponse({'result': "NO RH"})
    else:
        pprint.pprint(response.json())
    
        return JsonResponse({'result': response.json()['response']})


def get_cost_breakdown(request):
    """To get the cost breakdown data

    Args:
        request (get request): get request to get data.

    Returns:
        dict: Server's Cost Breakdown data.
    """
    
    request_body_dict = {}
    payload = json.loads(request.GET.get('body'))
    if payload['server_provider_type'] == 'aws':
        provider_account_id, volume_id_list, ami_id_list, id_list, \
            volume_list, flavor_id, os_family, region_name, region_code, \
            ip_list, status_of_server = get_server_data(payload=payload)

        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['ips'] = ip_list
        request_body_dict['resource_id'] \
            = ip_list + [payload["instance_id"]] + volume_id_list
        request_body_dict['volume_ids'] = volume_id_list
        request_body_dict['instance_id'] = [payload["instance_id"]]
        request_body_dict['start_date'] = payload['start_date']
        request_body_dict['end_date'] = payload['end_date']
        
        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                        request_body_dict, 
                        'get_server_cost_breakdown').fetch_response()
        
    elif payload['server_provider_type'] == 'azure_arm':
        provider_account_id, vm_id, disk_ids, region_code, \
            resource_group, ips = get_server_data(payload=payload)

        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['region_code'] = region_code
        request_body_dict['resource_group'] = resource_group
        request_body_dict['vm_id'] = vm_id
        request_body_dict['ips'] = ips
        request_body_dict['disk_ids'] = disk_ids
        request_body_dict['start_date'] = payload['start_date']
        request_body_dict['end_date'] = payload['end_date']
        
        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                        request_body_dict, 
                        'get_azure_cost_breakdown',
                        request_type="POST").fetch_response()
        
    if response.status_code == 422:
        return JsonResponse({'result': "NO RH"})
    else:
        pprint.pprint(response.json())
    
        return JsonResponse({'result': response.json()['response']})


def get_operational_cost(request):
    """To get the operational cost breakdown data

    Args:
        request (get request): get request to get data.

    Returns:
        dict: Server's Operational Cost Breakdown data.
    """
    
    request_body_dict = {}
    payload = json.loads(request.GET.get('body'))
    if payload['server_provider_type'] == 'aws':
        provider_account_id, volume_id_list, ami_id_list, id_list, \
            volume_list, flavor_id, os_family, region_name, region_code, \
            ip_list, status_of_server = get_server_data(payload=payload)
        
        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['instance_id'] = [payload["instance_id"]]
        request_body_dict['resource_id'] = ip_list + [payload["instance_id"]]
        request_body_dict['volume_ids'] = volume_id_list
        request_body_dict['amis'] = ami_id_list
        request_body_dict['start_date'] = payload['start_date']
        request_body_dict['end_date'] = payload['end_date']
        request_body_dict['region_code'] = region_code
        
        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                        request_body_dict, 
                        'get_server_operational_cost_breakdown').fetch_response()
        
    if response.status_code == 422:
        return JsonResponse({'result': "NO RH"})
    else:
        pprint.pprint(response.json())
    
        return JsonResponse({'result': response.json()['response']})


def get_potential_savings(request):
    """To get the operational potential savings data

    Args:
        request (get request): get request to get data.

    Returns:
        dict: Server's Potential Savings data.
    """
    
    request_body_dict = {}
    payload = json.loads(request.GET.get('body'))
    if payload['server_provider_type'] == 'aws':
        provider_account_id, volume_id_list, ami_id_list, id_list, \
            volume_list, flavor_id, os_family, region_name, region_code, \
            ip_list, status_of_server = get_server_data(payload=payload)
        
        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['volume_ids'] = volume_id_list
        request_body_dict['amis'] = ami_id_list
        request_body_dict['instance_id'] = [payload["instance_id"]]
        
        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                        request_body_dict, 
                        'get_potential_savings').fetch_response()
        
    elif payload['server_provider_type'] == 'azure_arm':
        provider_account_id, vm_id, disk_ids, region_code, \
            resource_group, ips = get_server_data(payload=payload)
        
        request_body_dict['provider_account_id'] = provider_account_id
        request_body_dict['vm_id'] = vm_id
        request_body_dict['disk_ids'] = disk_ids
        request_body_dict['region_code'] = region_code
        request_body_dict['resource_group'] = resource_group
        
        pprint.pprint(request_body_dict)
        
        response = ApiResponse(
                        request_body_dict, 
                        'azure_server_potential_savings').fetch_response()
        
    if response.status_code == 422:
        return JsonResponse({'result': "NO RH"})
    else:
        pprint.pprint(response.json())
    
        return JsonResponse({'result': response.json()})
