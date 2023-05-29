from infrastructure.views import server_refresh_stats
from infrastructure.models import Environment, Server
from common.methods import set_progress
from django.urls import reverse


def run(job, *args, **kwargs):
    set_progress("This code runs through the servers and refreshes the stats")
    try:
        aws_envs = Environment.objects.filter(
            resource_handler__resource_technology__modulename__startswith="resourcehandlers.aws"
        )
        vmware_envs = Environment.objects.filter(
            resource_handler__resource_technology__modulename__startswith="resourcehandlers.vmware"
        )
        # AWS Envs
        for aws_env in aws_envs:
            set_progress(f"Refreshing AWS stats for {aws_env}")
            servers = Server.objects.filter(environment__id=aws_env.id)
            for server in servers:
                server_id = server.id
                reverse("server_refresh_stats", args=[server_id])

        # VMWare Envs
        for vmware_env in vmware_envs:
            set_progress(f"Refreshing VMWare stats for {vmware_env}")
            servers = Server.objects.filter(environment__id=vmware_env.id)
            for server in servers:
                server_id = server.id
                reverse("server_refresh_stats", args=[server_id])

    except Exception as e:
        return "FAILURE", "Server Stats Refresh Failed", f"{e}"
    return "SUCCESS", "Server Stats Refreshed", ""
