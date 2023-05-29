# from resourcehandlers.openstack.gnocchi_wrapper import (
#    TechnologyWrapper as VMDetailsWrapper,
# )
import requests
import datetime
from api.v3.internal_api_client import InternalAPIClient
from django.contrib.auth.models import User
from infrastructure.models import Server
from resourcehandlers.models import ResourceHandler


admin_user = User.objects.filter(is_superuser=True, is_active=True).first()
api_client = InternalAPIClient(admin_user, "http", "localhost:8001", "80")


class VMDetailsWrapper:
    def __init__(self, resource_handler):
        self.resource_handler = resource_handler

    def _get_service_port(self, rh, *services):
        # implementation details
        return rh.port


def get_base_url(resource_handler, service):
    port = VMDetailsWrapper._get_service_port(
        resource_handler, resource_handler, service
    )

    if not "volume" in service:
        return f"{resource_handler.protocol}://{resource_handler.ip}:{port}"
    return f"{resource_handler.protocol}://{resource_handler.ip}:{port}"


def get_vm_basic_inventory(start_date, end_date, server):
    # base_url = get_base_url(resource_handler, "compute")
    # url = f"{base_url}/servers/{server.resource_handler_svr_id}/diagnostics"
    # headers = {
    #    "X-auth-token": resource_handler.api_auth_token,
    #    "Accept": "application/json",
    #    "Content-Type": "application/json",
    #    "X-OpenStack-Nova-API-Version": "2.48",
    # }
    # if resource_handler._check_token_validation():
    #    headers["X-auth-token"] = resource_handler.api_auth_token
    # else:
    #    token = resource_handler._generate_token()
    #    headers["X-auth-token"] = token

    # response = requests.get(
    #    url, headers=headers, verify=resource_handler.enable_ssl_verification
    # )
    # response = api_client.get(url)
    # if response.status_code == 200:
    #    response = response.json()

    server = Server.objects.get(id=server.id)
    srv_stats = server.get_resource_history(
        datetime.datetime(2023, 5, 1), datetime.datetime(2023, 5, 9)
    )
    tagids = server.resource_handler.taggableattribute_set.all()
    tags = ""
    if len(tagids) > 0:
        for tagid in tagids:
            tag_name = tagid.attribute
            if len(server.custom_field_values.filter(field__name=tag_name)) > 0:
                tag = server.custom_field_values.filter(field__name=tag_name)[
                    0
                ].str_value
                tags = tags + f"<b>{tag_name}</b>: {tag}<br>"
    os_build_name = ""
    if getattr(server, "os_build", None):
        os_build_name = server.os_build.name
    server_dict = {
        "id": server.id,
        "name": server.hostname,
        "cpu": server.cpu_cnt,
        "memory": server.mem_size,
        "disk": server.disk_size,
        "os": os_build_name,
        "uptime_in_days": round(srv_stats["cpu_hrs_on"] / 86400, 2),
        "uptime_in_hours": round(srv_stats["cpu_hrs_on"] / 3600, 2),
        "uptime_in_minutes": round(srv_stats["cpu_hrs_on"] / 60, 2),
        "Rate": format(server.rate, ".2f"),
        "Tags": tags,
    }
    return server_dict
    # else:
    #     raise Exception(f"{response.status_code} Something went wrong")


def get_optimization_report(resource_handler):
    rh = ResourceHandler.objects.get(id=resource_handler.id)
    rhc = rh.cast()
    serversList = []
    for server in rhc.server_set.all():
        server = Server.objects.get(id=server.id)
        srv_stats = server.get_resource_history(
            datetime.datetime(2023, 5, 1), datetime.datetime(2023, 5, 9)
        )
        os_build_name = ""
        if getattr(server, "os_build", None):
            os_build_name = server.os_build.name
        serversList.append(
            {
                "id": server.id,
                "name": server.hostname,
                "cpu": server.cpu_cnt,
                "memory": server.mem_size,
                "disk": server.disk_size,
                "os": os_build_name,
                "uptime_in_days": round(srv_stats["cpu_hrs_on"] / 86400, 2),
                "uptime_in_hours": round(srv_stats["cpu_hrs_on"] / 3600, 2),
                "uptime_in_minutes": round(srv_stats["cpu_hrs_on"] / 60, 2),
            }
        )
    return serversList


def calculate_snapshot_age(created_at):
    created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
    datetime_now = datetime.now()
    diff = datetime_now - created_at
    return diff.days
