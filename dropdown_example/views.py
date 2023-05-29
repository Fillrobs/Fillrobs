import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from infrastructure.models import Environment, Server
from resourcehandlers.models import ResourceHandler
from extensions.views import report_extension
from utilities.decorators import json_view
from utilities.templatetags import helper_tags
from utilities.logger import ThreadLogger

from .forms import ResourceHandlerForm

LOGGER = ThreadLogger(__name__)


@report_extension(title="Dropdown Example")
def dropdown_example(request):
    # Show table
    show_table = False
    resourceHandler = ""
    profile = request.get_user_profile()
    envs = Environment.objects_for_profile(profile)
    list_of_envs = [env.resource_handler for env in envs if env.resource_handler and env.resource_handler.resource_technology.type_slug in ['aws', 'azure_arm']]
    allowed_rts = set(list_of_envs)
    column_headings = [
        "Server Name",
        "Server Data",
        "Power Status",
    ]
    rows = []
    
    if request.method == "GET":
        form = ResourceHandlerForm(initial=dict(resourceHandler=resourceHandler))
    else:

        form = ResourceHandlerForm(request.POST)
        if form.is_valid():
            return_code = ""
            system_status = ""
            show_table = True
            # get the id of the selected resourceHandler
            resourceHandler = form.cleaned_data["resourceHandler"]
            if resourceHandler in allowed_rts:
                rh = ResourceHandler.objects.filter(id=resourceHandler).first()
            
                # logger.info(f"instancestatuses = {instancestatuses}")
                servers = Server.objects.filter(
                    resource_handler_id=resourceHandler, status="Active"
                )
                numinstances = len(servers)
                for srv in servers:
                    srvdata = ''
                    # logger.info(f"srvname = {srv.hostname}")
                    rhsrvid = srv.resource_handler_svr_id
                    # logger.info(f"{srv.hostname} = {rhsrvid}")
                    # logger.info(f"numinstances = {numinstances}")
                    srvip = srv.ip
                    srvmac = srv.mac
                    srvcpu_cnt = srv.cpu_cnt
                    srvmem_size = srv.mem_size 
                    get_memsize = '{0:.2g}'.format(srvmem_size)
                    chkfordot = '.'
                    if chkfordot in str(get_memsize):
                        splmem  = get_memsize.split(".")
                        if str(splmem[0]) == '0':
                            formatted_memsize = get_memsize
                        else:
                            formatted_memsize = splmem[0]
                    else:
                        formatted_memsize = get_memsize    
                    srvdata = '<b>IP:</b>&nbsp;{}<br><b>MAC:</b>&nbsp;{}<br><b>CPU:</b>&nbsp;{}<br><b>MEM:</b>&nbsp;{}'.format(srvip, srvmac, srvcpu_cnt, formatted_memsize + "GB")
                
                    rows.append(
                                (
                                srv.hostname,
                                srvdata,
                                srv.power_status,
                                )
                                )
                return_code = ""    
            else:
                        
                return_code = 500
    return render(
        request,
        "dropdown_example/templates/special.html",
        dict(
            show_table=show_table,
            allowed_rts=allowed_rts,
            form=form,
            pagetitle="Server Health Status Report",
            report_slug="Server Health Status Table",
            intro="""
            Server Health Status Extension.
            """,
            table_caption="Server Health Status Data",
            column_headings=column_headings,
            rows=rows,
        ),
   )     