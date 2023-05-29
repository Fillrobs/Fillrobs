"""
This plugin pulls data from CloudBolt to show servers for the selected  
All userResource Handlers
created on: 2023-05-03 by P Robins
"""
import boto3
import os
import shutil
import json
import datetime
from datetime import datetime, timedelta
from builtins import zip, next, object
from django.http import JsonResponse
import requests
from api.v3.internal_api_client import InternalAPIClient
from django.utils.translation import ugettext as _, ungettext
from django.shortcuts import render

from extensions.views import report_extension, ReportExtensionDelegate
from accounts.models import Group, Role, GroupRoleMembership
from infrastructure.models import ResourceHandler, Environment, Server
from resourcehandlers.aws.models import AWSHandler
from resourcehandlers.models import ResourceTechnology
from resourcehandlers.vmware.models import VsphereResourceHandler
from utilities.logger import ThreadLogger
from django.contrib.auth.models import User

from xui.maxis_server_utilization_report.gnocchi_wrapper import (
    TechnologyWrapper as VMDetailsWrapper,
)
from xui.maxis_server_utilization_report.utils import (
    get_vm_basic_inventory,
    get_optimization_report,
)
from .forms import MaxisCustomerForm

logger = ThreadLogger(__name__)


admin_user = User.objects.filter(is_superuser=True, is_active=True).first()
api_client = InternalAPIClient(admin_user, "http", "localhost:8001", "80")


def _set_report_thumbnails():
    """
    To set the report thumbnails
    """
    from settings import PROSERV_DIR

    dst_dir = os.path.join(
        PROSERV_DIR,
        "static",
        "uploads",
        "extensions",
        "maxis_server_utilization_report",
    )
    isExist = os.path.exists(dst_dir)
    if not isExist:
        os.makedirs(dst_dir)
    src_dir = os.path.join(
        PROSERV_DIR, "xui/maxis_server_utilization_report/static/images"
    )
    thumbnails = ["optimization_report.png", "monthly_performance_report.png"]
    for thumbnail in thumbnails:
        src = f"{src_dir}/{thumbnail}"
        dst = f"{dst_dir}/{thumbnail}"
        shutil.copyfile(src, dst)


class maxis_server_utilization_report_Delegate(ReportExtensionDelegate):
    def should_display(self):
        _set_report_thumbnails()
        can_view = self.viewer.is_super_admin
        if can_view == False:
            user_id = self.viewer.id
            # get the role id of customer_admin
            cust_admin_obj = Role.objects.filter(name="cust_admin").last()
            customer_admin_id = cust_admin_obj.id
            # Look to see if the user has these permissions
            grm = GroupRoleMembership.objects.filter(
                role_id=customer_admin_id, profile_id=user_id
            ).first()
            try:
                if grm.id:
                    can_view = True
            except AttributeError:
                can_view = False
        return can_view


@report_extension(
    title="Maxis Server Utilization Report",
    delegate=maxis_server_utilization_report_Delegate,
    thumbnail="maxis_server_utilization_report/monthly_performance_report.png.png",
)
def maxis_server_utilization_report(request):
    """
    This shows a list of the hosts

    """
    logger.info("Start of maxis_server_utilization_report")
    logger.info(f"request = {request}")
    # Show table
    show_table = False
    resourceHandler = ""
    maxis_customer = ""
    start_date = ""
    end_date = ""
    serversArr = []
    column_headings = [
        "Resource Handler",
        "Server Name",
        "Server Data",
        "Group",
        "Zone",
        "Power Status",
        "System Reachability Status",
        "Cost",
        "Tags",
    ]
    csv_column_headings = [
        "Resource Handler",
        "Server Name",
        "Group",
        "Zone",
        "Power Status",
        "System Reachability Status",
        "Cost",
        "Tags",
    ]
    rows = []

    profile = request.get_user_profile()
    my_profile_id = profile.id
    # if not profile.super_admin:
    #    raise PermissionDenied("Only super admins can view this report.")
    if request.method == "GET":
        form = MaxisCustomerForm(
            initial=dict(maxis_customer=maxis_customer, my_profile_id=my_profile_id)
        )
    else:
        form = MaxisCustomerForm(request.POST, my_profile_id=my_profile_id)

        if form.is_valid():
            data = form.cleaned_data
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            # logger.info(f"maxis_customer Chosen = {form.cleaned_data}")
            selected_group_id = form.cleaned_data["maxis_customer"]
            sel_grp = Group.objects.get(id=selected_group_id)
            return_code = ""
            system_status = ""
            show_table = True
            # get all of the AWS ResourceHandlers  for this group
            list_of_aws_envs = []
            for env in sel_grp.environments.all():
                if env.resource_handler.resource_technology.type_slug == "aws":
                    list_of_aws_envs.append(env)
            aws_rts = set(list_of_aws_envs)

            for environment in aws_rts:
                #  GET AWS Instance Data use boto3
                rh_id = environment.resource_handler.id
                rh_name = environment.resource_handler.name
                instancestatuses = []

                servers = Server.objects.filter(
                    resource_handler_id=rh_id,
                    environment=environment,
                    status="ACTIVE",
                    group=sel_grp,
                )
                wrapper = resourceHandler.get_api_wrapper()
                instancestatuses = []
                for region in set(
                    [env.aws_region for env in resourceHandler.environment_set.all()]
                ):
                    # logger.info(f"region={region}")
                    client = wrapper.get_boto3_client(
                        "ec2",
                        resourceHandler.serviceaccount,
                        resourceHandler.servicepasswd,
                        region_name=region,
                    )
                    instancestatuses.append(
                        client.describe_instance_status(IncludeAllInstances=True)[
                            "InstanceStatuses"
                        ]
                    )

                numinstances = len(instancestatuses[0])
                # logger.info(f"instancestatuses = {instancestatuses}")
                servers = Server.objects.filter(
                    resource_handler_id=resourceHandler, status="ACTIVE"
                )

                for srv in servers:
                    srv_data = ""
                    # logger.info(f"srv_name = {srv.hostname}")
                    rh_srv_id = srv.resource_handler_svr_id
                    # logger.info(f"{srv.hostname} = {rh_srv_id}")
                    # logger.info(f"numinstances = {numinstances}")
                    # tags
                    tagids = srv.resource_handler.taggableattribute_set.all()
                    tags = ""
                    if len(tagids) > 0:
                        for tagid in tagids:
                            tag_name = tagid.attribute
                            if (
                                len(
                                    srv.custom_field_values.filter(field__name=tag_name)
                                )
                                > 0
                            ):
                                tag = srv.custom_field_values.filter(
                                    field__name=tag_name
                                )[0].str_value
                                tags = tags + f"<b>{tag_name}</b>: {tag}<br>"
                    srv_cost = format(srv.rate, ".2f")
                    srv_ip = srv.ip
                    srv_mac = srv.mac
                    srv_cpu_cnt = srv.cpu_cnt
                    srv_mem_size = srv.mem_size
                    srv_disk_size = srv.disk_size
                    serversArr.append(get_vm_basic_inventory(start_date, end_date, srv))
                    get_memsize = "{0:.2g}".format(srv_mem_size)
                    chk_fordot = "."
                    if chk_fordot in str(get_memsize):
                        spl_mem = get_memsize.split(".")
                        if str(spl_mem[0]) == "0":
                            formatted_memsize = get_memsize
                        else:
                            formatted_memsize = spl_mem[0]
                    else:
                        formatted_memsize = get_memsize
                    srv_data = "<b>IP:</b>&nbsp;{}<br><b>MAC:</b>&nbsp;{}<br><b>CPU:</b>&nbsp;{}<br><b>MEM:</b>&nbsp;{}<br><b>Disk Size:</b>&nbsp;{}".format(
                        srv_ip,
                        srv_mac,
                        srv_cpu_cnt,
                        formatted_memsize + "GB",
                        srv_disk_size,
                    )
                    if numinstances > 0:
                        # loop through the collection
                        for i in instancestatuses:
                            # loop through the servers in each region
                            for j in i:
                                aws_zone = j["AvailabilityZone"]
                                InstanceId = j["InstanceId"]
                                # logger.info(f"InstanceId = {InstanceId}")
                                if InstanceId == rh_srv_id:
                                    # print(InstanceId)
                                    return_code = j["InstanceState"]["Name"]
                                    # print(return_code)
                                    try:
                                        system_status = j["InstanceStatus"]["Details"][
                                            0
                                        ]["Status"]

                                    except:
                                        system_status = j["InstanceStatus"]["Status"]
                                    rows.append(
                                        (
                                            rh_name,
                                            srv.hostname,
                                            srv_data,
                                            srv.group,
                                            aws_zone,
                                            return_code,
                                            system_status,
                                            srv_cost,
                                            tags,
                                        )
                                    )
                                    return_code = ""

            # get all of the VMware ResourceHandlers  for this user
            list_of_vmware_envs = []
            for env in sel_grp.environments.all():
                if env.resource_handler.resource_technology.type_slug == "vmware":
                    list_of_vmware_envs.append(env)

            vmware_rts = set(list_of_vmware_envs)
            # logger.info(f"vmware_rts = {vmware_rts}")
            for environment in vmware_rts:
                #  GET VMware Instance Data
                rh_id = environment.resource_handler.id
                rh_name = environment.resource_handler.name
                instancestatuses = []

                servers = Server.objects.filter(
                    resource_handler_id=rh_id,
                    environment=environment,
                    status="ACTIVE",
                    group=sel_grp,
                )
                numinstances = len(servers)
                for srv in servers:
                    srv_data = ""
                    # logger.info(f"srv_name = {srv.hostname}")
                    rh_srv_id = srv.resource_handler_svr_id
                    # logger.info(f"{srv.hostname} = {rh_srv_id}")
                    # logger.info(f"numinstances = {numinstances}")

                    # tags
                    tagids = srv.resource_handler.taggableattribute_set.all()
                    tags = ""
                    if len(tagids) > 0:
                        for tagid in tagids:
                            tag_name = tagid.attribute
                            if (
                                len(
                                    srv.custom_field_values.filter(field__name=tag_name)
                                )
                                > 0
                            ):
                                tag = srv.custom_field_values.filter(
                                    field__name=tag_name
                                )[0].str_value
                                tags = tags + f"<b>{tag_name}</b>: {tag}<br>"
                    srv_cost = format(srv.rate, ".2f")
                    srv_ip = srv.ip
                    srv_mac = srv.mac
                    srv_cpu_cnt = srv.cpu_cnt
                    srv_mem_size = srv.mem_size
                    serversArr.append(get_vm_basic_inventory(start_date, end_date, srv))
                    get_memsize = "{0:.2g}".format(srv_mem_size)
                    chk_fordot = "."
                    srv_disk_size = srv.disk_size
                    if chk_fordot in str(get_memsize):
                        spl_mem = get_memsize.split(".")
                        if str(spl_mem[0]) == "0":
                            formatted_memsize = get_memsize
                        else:
                            formatted_memsize = spl_mem[0]
                    else:
                        formatted_memsize = get_memsize
                    srv_data = "<b>IP:</b>&nbsp;{}<br><b>MAC:</b>&nbsp;{}<br><b>CPU:</b>&nbsp;{}<br><b>MEM:</b>&nbsp;{}<br><b>Disk Size:</b>&nbsp;{}".format(
                        srv_ip,
                        srv_mac,
                        srv_cpu_cnt,
                        formatted_memsize + "GB",
                        srv_disk_size,
                    )
                    rows.append(
                        (
                            rh_name,
                            srv.hostname,
                            srv_data,
                            srv.group,
                            "N/A",
                            "N/A",
                            "N/A",
                            srv_cost,
                            tags,
                        )
                    )
                    return_code = ""
            # logger.info(f"rows = {rows}")

    return render(
        request,
        "maxis_server_utilization_report/templates/table.html",
        dict(
            show_table=show_table,
            form=form,
            pagetitle="Maxis Server Utilization Report",
            report_slug="Maxis Server Utilization Report Table",
            intro="""
            Maxis Server Utilization Report Extension.
            """,
            table_caption="*To Filter by Resource Handler, please use the search box",
            column_headings=column_headings,
            csv_column_headings=csv_column_headings,
            rows=rows,
            servers=serversArr,
            start_date=start_date,
            end_date=end_date,
        ),
    )


def monthly_optimization_report(request):
    snapshots = []
    resource_handlers = ResourceHandler.objects.all()
    for resource_handler in resource_handlers:
        snapshots.extend(get_optimization_report(resource_handler))
    return render(
        request,
        "maxis_server_utilization_report/templates/optimization_report.html",
        {"pagetitle": "Server Optimization Report", "snapshots": snapshots},
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


def server_avg_utilization_graph(request):
    """
    Horizontal bar graph report.

    CPU, Memory, Disk and Network.

    HTTP GET Args
        period: one of 'year', 'month', 'week', 'day', 'hour'
    """

    profile = request.get_user_profile()

    # period is user-selectable
    period = request.GET.get("period", "month")
    periods = {
        "year": _("Year"),
        "month": _("Month"),
        "week": _("Week"),
        "day": _("Day"),
        "hour": _("Hour"),
    }
    period_label = periods.get(period)

    metric = request.GET.get("metric", "cpu")
    metrics = {
        "cpu": _("CPU"),
        "mem": _("Memory"),
        "disk": _("Disk"),
        "net": _("Network"),
    }
    metric_label = metrics.get(metric)
    metric_over_period = "avg_{}_last_{}".format(metric, period)

    if metric in ["cpu", "mem"]:
        metric_unit = "%"
    else:
        metric_unit = _("kB/s")

    yaxis_title = _("{metric} ({unit})").format(metric=metric_label, unit=metric_unit)

    rh_ids_to_exclude = []
    if period == "year" or metric == "mem":
        rh_ids_to_exclude.extend([rh.id for rh in AWSHandler.objects.all()])
    if period == "week":
        rh_ids_to_exclude.extend([rh.id for rh in VsphereResourceHandler.objects.all()])

    categories = []
    values = []
    my_active_servers = (
        Server.objects_for_profile(profile)
        .exclude(status="HISTORICAL")
        .exclude(resource_handler_id__in=rh_ids_to_exclude)
        .values_list("id", flat=True)
    )

    all_stats = (
        ServerStats.objects.filter(server_id__in=my_active_servers)
        .order_by(metric_over_period)
        .select_related("server")
    )
    for stats in all_stats:
        value = getattr(stats, metric_over_period, 0) or 0
        categories.append(escape(stats.server.hostname))

        # keep any negative averages out of this chart, which is possible if
        # VMware or AWS provides a dataset of entirely -1s over a time period
        if float(value) >= 0:
            values.append(float(value))
        else:
            values.append(0)

    if categories and values:
        # sort by usage, in descending order. categories (aka hostnames) and values both need to be sorted this way
        values, categories = (
            list(t) for t in zip(*sorted(zip(values, categories), reverse=True))
        )

    # We could show just the top 150 bars
    # categories = categories[:150]
    # values = values[:150]

    # Because there may be a large number of bars (categories), dynamically determine a good
    # height for the chart container. 100px per 25 bars.
    height = 800 + (200 * len(categories) / 25)

    title = _("Average {metric} over the last {time_period} ({units})").format(
        metric=metric_label, time_period=period_label.lower(), units=metric_unit
    )
    return render(
        request,
        "reports/internal/server_avg_utilization_graph.html",
        dict(
            pagetitle=title,
            report_slug="Average {metric} usage over the last {time_period} ({unit})".format(
                metric=metric, time_period=period, unit=metric_unit
            ),
            subtitle=_(
                "Showing {server_count} active servers you have permission to " "view."
            ).format(server_count=len(categories)),
            # Y-axis is the horizontal one in this chart
            yaxis_title=yaxis_title,
            # Chart data
            categories=categories,
            values=values,
            series_name=title,
            # Optionally support exporting as CSV by including this dict
            export=dict(csv_headings=["Server", title]),
            periods=periods,
            current_period=period,
            metrics=metrics,
            current_metric=metric,
            graph_height=height,
            # Fine tune padding between bars
            plot_options=dict(series=dict(pointPadding=0)),
        ),
    )
