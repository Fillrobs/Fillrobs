from django.conf.urls import url
from xui.maxis_server_utilization_report import views

xui_urlpatterns = [
    url(
        r"^maxis_server_utilization_report/(?P<group_id>\d+)/$",
        views.maxis_server_utilization_report,
        name="maxis_server_utilization_report",
    ),
    url(
        r"^maxis_server_utilization_report/get_utilization_report_data/$",
        views.get_utilization_report_data,
        name="get_utilization_report_data",
    ),
]
