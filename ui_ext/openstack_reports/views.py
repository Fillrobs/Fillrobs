from extensions.views import report_extension, ReportExtensionDelegate
from django.shortcuts import render
from infrastructure.models import ResourceHandler, Server

# from resourcehandlers.openstack.models import OpenStackHandler
from datetime import datetime, timedelta

from xui.openstack_reports.utils import get_vm_basic_inventory, get_optimization_report
from resourcehandlers.openstack.gnocchi_wrapper import (
    TechnologyWrapper as VMDetailsWrapper,
)
from django.http import JsonResponse
import json
import shutil
import os


def _set_report_thumbnails():
    """
    To set the report thumbnails
    """
    from settings import PROSERV_DIR

    dst_dir = os.path.join(
        PROSERV_DIR, "static", "uploads", "extensions", "openstack_reports"
    )
    isExist = os.path.exists(dst_dir)
    if not isExist:
        os.makedirs(dst_dir)
    src_dir = os.path.join(PROSERV_DIR, "xui/openstack_reports/static/images")
    thumbnails = ["optimization_report.png", "monthly_performance_report.png"]
    for thumbnail in thumbnails:
        src = f"{src_dir}/{thumbnail}"
        dst = f"{dst_dir}/{thumbnail}"
        shutil.copyfile(src, dst)


class OpenStackReportsDelegate(ReportExtensionDelegate):
    def should_display(self):
        _set_report_thumbnails()
        return True


@report_extension(
    title="OpenStack Monthly VM Reports",
    description="OpenStack Monthly Performance reports of VM, CPU utilization, Memory utilization and Network utilization",
    thumbnail="openstack_reports/monthly_performance_report.png",
    delegate=OpenStackReportsDelegate,
)
def monthly_performance_report(request):
    servers = []
    resource_handlers = ResourceHandler.objects.all()
    for resource_handler in resource_handlers:
        # amend to get servers from table/group
        rh_servers = resource_handler.server_set.exclude(status="HISTORICAL")
        for server in rh_servers:
            servers.append(get_vm_basic_inventory(resource_handler, server))
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    return render(
        request,
        "openstack_reports/templates/monthly_performance_report.html",
        {
            "pagetitle": "OpenStack Monthly VM Reports",
            "servers": servers,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@report_extension(
    title="OpenStack Optimization Report",
    description="OpenStack virtual machine with snapshots",
    thumbnail="openstack_reports/optimization_report.png",
    delegate=OpenStackReportsDelegate,
)
def monthly_optimization_report(request):
    snapshots = []
    resource_handlers = ResourceHandler.objects.all()
    for resource_handler in resource_handlers:
        snapshots.extend(get_optimization_report(resource_handler))
    return render(
        request,
        "openstack_reports/templates/optimization_report.html",
        {"pagetitle": "OpenStack Optimization Report", "snapshots": snapshots},
    )


def get_utilization_report_data(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("body"))
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        vm_id = data.get("vm_id")
        server = Server.objects.get(id=vm_id)
        resource_handler = server.resource_handler
        wrapper = VMDetailsWrapper(
            resource_handler.cast(),
            resource_handler.ip,
            server.resource_handler_svr_id,
            resource_handler.protocol,
        )
        metric_ids = wrapper._get_performance_metric_ids()
        usage_for_vms = wrapper.collect_vm_performance(
            "last_month", metric_ids, f"{start_date}T00:00", f"{end_date}T00:00"
        )
        return JsonResponse(
            {
                "result": usage_for_vms,
                "message_status": True,
                "start_date": datetime.strptime(start_date, "%Y-%m-%d"),
                "interval": 7200,
                "points": 360,
            }
        )
