from resourcehandlers.openstack.gnocchi_wrapper import (
    TechnologyWrapper as VMDetailsWrapper,
)
import requests
from datetime import datetime

def get_base_url(resource_handler, servie):
    port = VMDetailsWrapper._get_service_port(
        resource_handler, resource_handler, servie)
    if not "volume" in servie:
        return f"{resource_handler.protocol}://{resource_handler.ip}:{port}/{resource_handler.project_id}"
    return f"{resource_handler.protocol}://{resource_handler.ip}:{port}"


def get_vm_basic_inventory(resource_handler, server):
    base_url = get_base_url(resource_handler, "compute")
    url = f"{base_url}/servers/{server.resource_handler_svr_id}/diagnostics"
    headers = {
        "X-auth-token": resource_handler.api_auth_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-OpenStack-Nova-API-Version": "2.48"
    }
    if resource_handler._check_token_validation():
        headers["X-auth-token"] = resource_handler.api_auth_token
    else:
        token = resource_handler._generate_token()
        headers["X-auth-token"] = token
    response = requests.get(url, headers=headers,
                            verify=resource_handler.enable_ssl_verification)
    if response.status_code == 200:
        response = response.json()
        server_dict = {
            "id": server.id,
            "name": server.hostname,
            "cpu": server.cpu_cnt,
            "memory": server.mem_size,
            "disk": server.disk_size,
            "os": response['hypervisor_os'],
            "uptime_in_days": round(response['uptime']/86400, 2),
            "uptime_in_hours": round(response['uptime']/3600, 2),
            "uptime_in_minutes": round(response['uptime']/60, 2)
        }
        return server_dict
    else:
        raise Exception(f"{response.status_code} Something went wrong")


def get_optimization_report(resource_handler):
    base_url = get_base_url(resource_handler, "volumev3")
    url = f"{base_url}/snapshots/detail"
    headers = {
        "X-auth-token": resource_handler.api_auth_token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if resource_handler._check_token_validation():
        headers["X-auth-token"] = resource_handler.api_auth_token
    else:
        token = resource_handler._generate_token()
        headers["X-auth-token"] = token
    response = requests.get(url, headers=headers,
                            verify=resource_handler.enable_ssl_verification)
    if response.status_code == 200:
        response = response.json()
        snapshot_list = []
        for record in response['snapshots']:
            snapshot_dict = {}
            snapshot_dict["name"] = record['name'].replace("snapshot for ", "")
            snapshot_dict["snapshot_size"] = record['size']
            snapshot_dict["snapshot_age"] = calculate_snapshot_age(record['created_at']) if record['created_at'] else 0
            snapshot_dict["parent_project"] = record['os-extended-snapshot-attributes:project_id']
            snapshot_dict["status"] = record['status']
            snapshot_list.append(snapshot_dict)
        return snapshot_list
    else:
        raise Exception(f"{response.status_code} Something went wrong")


def calculate_snapshot_age(created_at):
    created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
    datetime_now = datetime.now()
    diff = datetime_now - created_at
    return diff.days


