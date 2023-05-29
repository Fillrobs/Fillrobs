import json
import datetime
import traceback
import requests

from django.core.cache import cache
from utilities.models import ConnectionInfo
from xui.kumo_integration_kit import kumo_wrapper
from xui.kumo_integration_kit.constants import (
    API_ENDPOINTS_DICT,
    DATA_BACKUP_HOURS
)


class ApiResponse:
    """
    To fetch and handle the response from the Kumolus API endpoints
    """
    def __init__(self, payload, api_endpoint, web_host=None, request_type=None):
        self.response = {}
        self.api_endpoint = API_ENDPOINTS_DICT[api_endpoint]
        self.payload = payload
        self.request_type = request_type
        self.web_host = web_host
        self.api_endpoint_key = api_endpoint
    
    def fetch_response(self):
        try:
            with kumo_wrapper.KumoConnector() as conn:
                if self.web_host:
                    conn.base_url = self.web_host
                    
                if self.request_type == "POST":
                    self.response = conn.post(self.api_endpoint, json=self.payload)
                else:
                    self.response = conn.get(self.api_endpoint, json=self.payload)
                
                if self.api_endpoint_key != 'validate_api_token' and \
                    self.api_endpoint_key != 'service_type_count':
                    self.response.raise_for_status()
                
                if self.api_endpoint_key not in \
                    ['get_csv_download', 'get_potential_savings',
                     'ec2_rightsizing_csv', 'azure_server_potential_savings',
                     'validate_api_token', 'service_type_count', 'azure_currency']:
                    try:
                        if 'message' in self.response.json().keys():
                            self.response = {}
                    except:
                        pass

        except:
            traceback.print_exc()
            if self.response.status_code == 422:
                pass
            else:
                self.response = {}
        
        return self.response


def get_credentials_from_db():
    """
    To fetch Kumolus credentials of customer from ConnectionInfo table

    Returns:
        str: customer's Kumolus domain and API Key
    """
    ci = ConnectionInfo.objects.filter(
        name__iexact='Kumolus Kit Creds').first()
    if ci:
        if ci.ip and ci.password:
            return f'https://{ci.ip}', ci.password    
    return "", ""


def get_adapter_id(account_id=None):
    """
    To fetch and return the adapters from Kumolus
    """
    aws_adapter, azure_adapters = {}, {}
    normal_adapter_id = ""
    payload = {
        'show_all': 'true',
        'not_configured': 'true',
    }
    
    response = ApiResponse(payload, 'get_mapped_adapters').fetch_response()
    if response:
        response = response.json()['_embedded']['adapter']
        
        aws_adapter = {adapter['aws_account_id']: adapter['id']
                    for adapter in response if 'aws_account_id' in adapter and adapter['aws_account_id']}

        azure_adapters = {adapter['azure_account_id']: adapter['id']
                        for adapter in response if 'azure_account_id' in adapter and adapter['azure_account_id']}

        if account_id:
            try:
                normal_adapter_id = aws_adapter[account_id] if account_id in aws_adapter.keys(
                ) else azure_adapters[account_id]
            except KeyError:
                pass    
                
    if account_id:
        return normal_adapter_id
    else:
        return aws_adapter, azure_adapters


def get_azure_currency(provider_account_id):
    """
    To fetch azure resource handler currency from Kumolus

    Args:
        provider_account_id (str): azure subscription id

    Returns:
        str: Currency in 3 char format e.g. USD, INR, etc.
    """
    payload = {"provider_account_id": provider_account_id}

    response = ApiResponse(payload, 'azure_currency').fetch_response()
    if response:
        response = response.text
    else:
        response = 'USD'
        
    return response


def check_for_cache(rh_file_name):
    """
    To check if cache exists

    Args:
        rh_file_name (str): Key name of the cache

    Returns:
        bool: if no cache exists then returns True to fetch
    """
    cached_data = cache.get(rh_file_name, 'NO-VALUE')
    if cached_data == 'NO-VALUE':
        return True
    else:
        return False


def get_cache_data(rh_file_name):
    """
    To fetch the cache if exists 

    Args:
        rh_file_name (str): Key name of the cache

    Returns:
        json: if cache exists returns the json object
    """
    cached_data = json.loads(cache.get(rh_file_name, 'NO-VALUE'))
    if cached_data != 'NO-VALUE':
        return cached_data
    else:
        return {}


def set_cache_data(rh_file_name, data_to_bo_stored):
    """
    To save the data in the cache

    Args:
        rh_file_name (str): Key name of the cache
        data_to_bo_stored (dict): python dictionary containing data to be cached
    """
    cache.set(rh_file_name, json.dumps(data_to_bo_stored), DATA_BACKUP_HOURS*60*60)
    return
