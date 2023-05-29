import json
import traceback

from resourcehandlers.aws.models import AWSHandler
from resourcehandlers.azure_arm.models import AzureARMHandler
from resourcehandlers.models import ResourceHandler
from xui.kumo_integration_kit.utils import ApiResponse
from utilities.decorators import json_view
from django.http import HttpResponse


@json_view
def cost_efficiency_for_rh(request):
    """
    To get the service adviser data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    charts_data = {}
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['rh_id']).cast()
    charts_data['service_type_summary'] = []
    
    if isinstance(rh, AWSHandler):
        
        if payload['service_type'] == "ec2_right_sizings" or \
            payload['service_type'] == "":
            response = ApiResponse(payload, 'ec2_rightsize').fetch_response()
            if response:
                charts_data['service_type_summary'].append({
                    'type': 'ec2_right_sizings',
                    'count': response.json()['meta_data']['instance_count'],
                    'cost_sum': response.json()['meta_data']['total_saving'],
                })
        
        if payload['service_type'] == "ignore_services" or \
            payload['service_type'] == "":
            response = ApiResponse(payload, 'ignored_services').fetch_response()
            if response:
                charts_data['service_type_summary'].append({
                    "type": "ignore_services",
                    "count": response.json()['count'],
                    "cost_sum": response.json()['service_cost_sum'],
                })
            
        response = ApiResponse(payload, 'service_type_count').fetch_response()
        if response:
            if 'message' in response.json():
                if not charts_data:
                    charts_data['message'] = "no normal adapter"
            else:    
                charts_data['service_type_summary'] += response.json()[
                    'service_type_count']
            
    elif isinstance(rh, AzureARMHandler):
        response = ApiResponse(payload, 'service_type_count').fetch_response()
        if response:
            if 'message' in response.json():
                if not charts_data:
                    charts_data['message'] = "no normal adapter"
            else:    
                charts_data['service_type_summary'] += response.json()[
                    'service_type_count']

    return charts_data


def csv_download_for_rh_json(request):
    """
    To download the services list from Kumolus in csv format

    Args:
        request (http request): request having various params

    Returns:
        text/csv: csv data to be downloaded on the front-end
    """
    payload = json.dumps(request.GET)
    payload = json.loads(payload)
    if payload['ec2_status'] == "true":
        response = ApiResponse(payload, 'ec2_rightsizing_csv').fetch_response()
    else:
        response = ApiResponse(payload, 'get_csv_download').fetch_response()
    if response:
        csv_data = HttpResponse(response.text, content_type='text/csv')
        csv_data['Content-Disposition'] = 'attachment; filename=recommendation.csv'
        return csv_data


@json_view
def region_list_for_rh_json(request):
    """
    To get the region and tag list from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having region and tag list
    """
    charts_data = {}
    payload = json.loads(request.body)

    response = ApiResponse(payload, 'get_regions_list').fetch_response()
    if response:
        response = response.json()['_embedded']['account_region']
        charts_data['regions_list'] = [
            {'enabled': regi['enabled'],
            'region_id': regi['region_id'],
            'region_name': regi['region_name'],
            'adapter_type': regi['adapter_type'],
            'code': regi['code'],
            } for regi in response
            if regi['adapter_type'].split('::')[1]
            == payload['handler_type']]
    else:
        charts_data['regions_list'] = []
        

    response = ApiResponse(payload, 'get_tags_list').fetch_response()
    if response:
        charts_data['tags_list'] = response.json()
    else:
        charts_data['tags_list'] =  {}  

    return charts_data


@json_view
def service_details_for_rh_json(request):
    """
    To get the detail of selected service type from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having service details of service type
    """
    payload = json.loads(request.body)

    response = ApiResponse(payload, 'get_mapped_adapters').fetch_response()
    if response:   
        response = response.json()
        adapters_dict = {adapter['id']: adapter['name']
                        for adapter in response['_embedded']['adapter']}

    response = ApiResponse(payload, 'get_regions_list').fetch_response()
    if response: 
        response = response.json()
        regions_dict = {region['region_id']: region['region_name']
                        for region in response['_embedded']['account_region']}

    if payload['service_type'] == 'ec2_right_sizings':
        response = ApiResponse(payload, 'ec2_rightsize').fetch_response()
        if response:
            response = {'services': response.json()['ec2_right_sizings']}
        else:
            response = {'services': []}
    else:
        response = ApiResponse(payload, 'get_service_type_details').fetch_response()
        if response:
            response = response.json()

            if payload['service_type'] == 'amis':
                response_amis = {'services': []}
                for items in response['amis']:
                    response_amis['services'].extend(items['results'])
                response = {'services': response_amis['services']}

            for services in response['services']:
                services['adapter_name'] = adapters_dict.get(
                    services['adapter_id'], 'N/A') if 'adapter_id' in services else 'N/A'
                services['region_name'] = regions_dict[services['region_id']]

    return response


@json_view
def ignored_services_list_for_rh_json(request):
    """
    To get the ignored services list from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having services list
    """
    payload = json.loads(request.body)

    # To fetch ignored service List with Details
    response = ApiResponse(payload, 'ignored_services').fetch_response()
    if response:
        response = response.json()
        
    return response


@json_view
def get_graph_data(request):
    """
    To get the graph data for selected service from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having graph data
    """
    payload = json.loads(request.body)

    response = ApiResponse(payload, 'get_graph_data',
                           request_type="POST").fetch_response()
    if response:
        response = response.json()

    return response
