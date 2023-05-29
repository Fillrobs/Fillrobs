import json
import traceback

from resourcehandlers.models import ResourceHandler
from xui.kumo_integration_kit import utils
from xui.kumo_integration_kit.utils import ApiResponse
from utilities.decorators import json_view
from utilities.permissions import cbadmin_required
from utilities.models import ConnectionInfo
from resourcehandlers.models import ResourceHandler
from django.http import HttpResponse, JsonResponse


class KumoKit(object):
    """
    Database object for Kumolus credentials
    """
    def __init__(self):
        ci = ConnectionInfo.objects.filter(
            name__iexact='Kumolus Kit Creds').first()
        if ci:
            self.connection_info = ci
            self.name = ci.name
            self.protocol = ci.protocol
            self.ip = ci.ip
            self.port = ci.port
            self.username = ci.username
            self.password = ci.password
            self.headers = ci.headers
        else:
            self.name = ""
            self.connection_info = ConnectionInfo()

    def save_credentials(self, *args, **kwargs):
        user_entry_object = ConnectionInfo(*args, **kwargs)
        kituser = user_entry_object.save()
        return kituser
    
    def update_credentials(self, *args, **kwargs):
        ip, password = kwargs["ip"], kwargs["password"]
        
        ci = ConnectionInfo.objects.filter(
            name__iexact='Kumolus Kit Creds').update(ip=ip, password=password)
        return ci
    
    def get_credentials(self):
        return self.connection_info


@json_view
@cbadmin_required
def validate_creds(request):
    """ To validate the credentials

    Args:
        request (http request): This function will validate the credentials
        entered by the customer for the first time before storing it in Cloudbolt database.
    """
    payload = json.loads(request.POST.get('body'))
    web_host = payload['web_host']
    api_key = payload['api_key']

    response = ApiResponse(payload, 'validate_api_token',
                            web_host=web_host).fetch_response()
    
    if response and response.json()['message'] == "success":
        status = True
    else:
        status = False

    return JsonResponse({'result': status})


@json_view
@cbadmin_required
def save_creds(request):
    """ To save the credentials

    Args:
        request (http request): This function will save the credentials
        entered by the customer after successful validation in Cloudbolt database.
    """
    payload = json.loads(request.POST.get('body'))
    print(payload)
    web_host = payload['web_host']
    api_key = payload['api_key']

    try:
        kumokit = KumoKit()
        if kumokit.name:
            if kumokit.ip == web_host.split("://")[1] and kumokit.password == api_key:
                status = True
                exists = True

                return JsonResponse({'result': status, 'exists': exists})
            else:
                kituser = kumokit.update_credentials(
                    ip=web_host.split("://")[1],
                    password=api_key)

                status = True
                changed = True
                
                return JsonResponse({'result': status, 'changed': changed})
        else:
            kituser = kumokit.save_credentials(
                name="Kumolus Kit Creds",
                protocol=web_host.split("://")[0],
                ip=web_host.split("://")[1],
                password=api_key)

        status = True

    except:
        traceback.print_exc()
        status = False

    return JsonResponse({'result': status})


@json_view
@cbadmin_required
def get_creds(request):
    """ To fetch the credentials

    Args:
        request (http request): This function will fetch the credentials
        stored by the customer in Cloudbolt database.
    """
    creds = {}

    try:
        kumokit = KumoKit()
        if kumokit.name:
            creds = {
                'web_host': kumokit.ip,
                'api_key': kumokit.password,
            }

            status = True
        else:
            status = False

    except:
        traceback.print_exc()
        status = False

    return JsonResponse({'result': status, 'creds': creds})


@json_view
@cbadmin_required
def get_rh_list(request):
    """ To fetch the list of Resource Handlers

    Args:
        request (http request): This function will fetch the resource handlers
        that already added by the customer in Cloudbolt account.
    """
    rh_list = ResourceHandler.objects.all()
    payload = json.loads(request.POST.get('body'))
    matched_rh_list = []

    try:
        kumokit = KumoKit()

        if kumokit.name:
            aws_adapter, azure_adapters = utils.get_adapter_id()

            print(aws_adapter)
            print(azure_adapters)

            matched_rh_list = []
            for rh in rh_list:
                rh_dict = ResourceHandler.objects.filter(
                    pk=rh.cast().id).values()[0]

                if 'account_id' in rh.cast().__dict__.keys():
                    if rh.cast().account_id in aws_adapter:
                        matched_rh_list.append(rh_dict)

                else:
                    if rh.cast().serviceaccount in azure_adapters:
                        matched_rh_list.append(rh_dict)
    except:
        traceback.print_exc()

    return JsonResponse({'result': matched_rh_list})


@json_view
@cbadmin_required
def save_kumo_data(request):
    """ To save Billing and Normal account Ids

    Args:
        request (http request): This function will store the billing and 
        normal ids entered by user in Cludbolt Database.
    """
    payload = json.loads(request.POST.get('body'))
    print(payload)
    existing_data = {}

    try:
        kumokit = KumoKit()
        if kumokit.name:
            if kumokit.headers:
                existing_data = json.loads(kumokit.headers)
                existing_data[payload['rhid']] = {
                    "billing_account": payload['billing_account'],
                    "normal_account": payload['normal_account'],
                }
            else:
                existing_data[payload['rhid']] = {
                    "billing_account": payload['billing_account'],
                    "normal_account": payload['normal_account'],
                }

            ConnectionInfo.objects.filter(name__iexact='Kumolus Kit Creds').update(
                headers=json.dumps(existing_data))
            status = True
        else:
            status = False

    except:
        traceback.print_exc()
        status = False

    return JsonResponse({'result': status})


@json_view
def validate_api_token(request):
    """
    To validate the Kumolus account's API key entered by the customer

    Args:
        request (http request): reuest having api key as params

    Returns:
        dict: having message for status of the validation
    """
    payload = json.loads(request.body)
    
    kumokit = KumoKit()
    if kumokit.name:
        payload['api_key'] = kumokit.password
    
    response = ApiResponse(payload, 'validate_api_token').fetch_response()
    if response:
        response = response.json()
        
    return JsonResponse({'result': response})


@json_view
def get_config(request):
    """
    To fetch the Kumolus account's config for service adviser 
    set by the customer

    Args:
        request (http request): None

    Returns:
        dict: having response with configuration data
    """
    payload = {}
    
    response = ApiResponse(payload, 'get_config').fetch_response()
    if response:
        response = response.json()
        
    return JsonResponse({'result': response})


@json_view
def set_config(request):
    """
    To set the Kumolus account's config for service adviser 
    set by the customer

    Args:
        request (http request): request with config data

    Returns:
        dict: having response with configuration data
    """
    payload = json.loads(request.POST.get('body'))
    
    response = ApiResponse(payload, 'get_config', 
                           request_type="POST").fetch_response()
    if response:
        response = response.json()
        
    return JsonResponse({'result': response})