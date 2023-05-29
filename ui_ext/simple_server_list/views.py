"""
Module contains all views for this extension package.
"""
import requests

from extensions.views import report_extension
from django.shortcuts import render
from infrastructure.models import Server
from infrastructure.templatetags import infrastructure_tags
from utilities.templatetags import helper_tags


@report_extension(title="Simple Server List", thumbnail='simple_server_list/serverlist.jpg')
def simple_server_list(request):
    rows = []
    column_headings = ['ID', 'Server', 'Status']
    for srv in Server.objects.filter(status='Active'):
        rows.append((srv.id, srv.hostname, 'Active'))
        
    # This sample extension renders a generic template for tabular reports,
    # which requires this view to return just a few context variables.
    #
    # You could also render your own template in '<package_name>/templates/special.html'
    # that extends one of the following and adds customizations:
    #     'reports/table.html' if you want a more customized data table
    #     'reports/simple_base.html' for more advanced customization, e.g. more
    #     than one chart or table.
    #     'base.html' to start from scratch from the basic CloudBolt template
    # return render(request, 'reports/table.html', dict(
        
    return render(
                request,
                "simple_server_list/reports/table.html",
                dict(
                    pagetitle="Simple Server REPORT",
                    report_slug="Custom-Server-Table",
                    intro="""
                    Sample report extension.
                    """,
                    column_headings=column_headings,
                    rows=rows,
                ),
            )
