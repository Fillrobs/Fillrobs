from django.conf.urls import url
from xui.openstack_reports.views import (
    get_utilization_report_data
)

xui_urlpatterns = [
    url(r"^xui/openstack_reports/get_utilization_report_data/$",
        get_utilization_report_data, name="get_utilization_report_data"),
]
