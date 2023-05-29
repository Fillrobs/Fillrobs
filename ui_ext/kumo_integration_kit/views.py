import os
import json

from django.core.management import call_command
from django.shortcuts import render, get_object_or_404
from extensions.views import admin_extension, tab_extension, TabExtensionDelegate
from resourcehandlers.models import ResourceHandler
from resourcehandlers.aws.models import AWSHandler
from resourcehandlers.azure_arm.models import AzureARMHandler
from utilities.logger import ThreadLogger
from xui.kumo_integration_kit import utils
from utilities.models import ConnectionInfo
from infrastructure.models import Server
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

logger = ThreadLogger(__name__)


def _collect_static():
    """
    To call the collectstatic method internally when XUI is installed
    """
    from settings import PROSERV_DIR
    src = os.path.join(PROSERV_DIR, "xui/kumo_integration_kit/static")
    dst = os.path.join(PROSERV_DIR, "static/kumo_integration_kit")

    try:
        os.symlink(src, dst)
        call_command('collectstatic', '--no-input')
    except FileExistsError:
        pass


class ResourceHandlerTabBaseClass(TabExtensionDelegate):
    """
    To control the visibility of the resource handler tabs
    """
    def should_display(self):
        rh = self.instance.cast()
        ci = ConnectionInfo.objects.filter(name__iexact='Kumolus Kit Creds')

        if ci:
            if ci.first().ip and ci.first().password:
                return isinstance(rh, AWSHandler) or isinstance(rh, AzureARMHandler)
        else:
            return False


class ServerTabBaseClass(TabExtensionDelegate):
    """
    To control the visibility of the server tabs
    """
    def should_display(self):
        try:
            server_instance = self.instance.resource_handler.type_slug
            if server_instance == "aws" or server_instance == "azure_arm":
                return True
        except:
            pass
        return False
    
    
class HandlerInitializer:
    """ 
    To compute the initial variables when a resource handler tab is shown.
    """
    def __init__(self, resource_handler) -> None:
        self.resource_handler = resource_handler
        
    def get_handler(self):
        return get_object_or_404(ResourceHandler, pk=int(self.resource_handler)).cast()
    
    def get_handler_type(self):
        return "AWS" if isinstance(self.handler, AWSHandler) else "Azure"
    
    def get_provider_account_id(self):
        return str(self.handler.account_id) if self.handler_type == "AWS" else str(self.handler.serviceaccount)

    def get_rh_currency(self):
        return utils.get_azure_currency(self.provider_account_id) if self.handler_type == "Azure" else "USD"
    
    def get_customer_credentials(self):
        return utils.get_credentials_from_db()
    
    def get_kumo_adapter_id(self):
        return utils.get_adapter_id(str(self.provider_account_id)) if self.provider_account_id and self.KUMO_WEB_HOST else ""
    
    def initialize(self):
        self.handler = self.get_handler()
        self.handler_type = self.get_handler_type()
        self.provider_account_id = self.get_provider_account_id()
        self.currency = self.get_rh_currency()
        self.KUMO_WEB_HOST, self.KUMO_API_KEY = self.get_customer_credentials()
        self.kumo_adapter_id = self.get_kumo_adapter_id()
        return self
        

@tab_extension(model=ResourceHandler, title="Spend",
               description='Cost details of Resource Handler', 
               delegate=ResourceHandlerTabBaseClass)
def display_a_tab(request, resource_handler):
    """
    To display Spend tab in resource handler

    Args:
        request (http request)
        resource_handler (int): selected resource handlers id

    Returns:
        html: renders html file python dictionary with various required pramaeters
    """
    rh = HandlerInitializer(resource_handler=resource_handler).initialize()
    return render(request, 'kumo_integration_kit/templates/spendings.html',
                  {'handler_type': rh.handler_type,
                   'rh_id': rh.handler.id,
                   'acc_currency': rh.currency,
                   'handler_normal_id': rh.provider_account_id,
                   'normal_adapter_id': rh.kumo_adapter_id,
                   'KUMO_WEB_HOST': rh.KUMO_WEB_HOST})


@tab_extension(model=ResourceHandler, title="Efficiency",
               description='Services details of Resource Handler',
               delegate=ResourceHandlerTabBaseClass)
def display_b_tab(request, resource_handler):
    """
    To display Efficiency tab in resource handler

    Args:
        request (http request)
        resource_handler (int): selected resource handlers id

    Returns:
        html: renders html file python dictionary with various required pramaeters
    """
    rh = HandlerInitializer(resource_handler=resource_handler).initialize()
    return render(request, 'kumo_integration_kit/templates/efficiency.html',
                  {'handler_type': rh.handler_type,
                   'rh_id': rh.handler.id,
                   'acc_currency': rh.currency,
                   'handler_normal_id': rh.provider_account_id,
                   'normal_adapter_id': rh.kumo_adapter_id,
                   'KUMO_WEB_HOST': rh.KUMO_WEB_HOST})


@tab_extension(
    title='Costs',  # `title` is what end users see on the tab
    description='Server related cost details',
    model=Server, # Required: the model this extension is for
    delegate=ServerTabBaseClass
)
def display_server(request, obj_id):
    """
    To display the detailed billing data on server tab.
    """
    # Instantiate the server instance using the ID passed in.
    server = Server.objects.get(id=obj_id)
    server_data = {
        'resource_handler_svr_id': server.resource_handler_svr_id,
        'id': server.id,
        'type_slug': server.resource_handler.resource_technology.type_slug
    }
    json_parsed_data = json.dumps(server_data)
    return render(request, 'kumo_integration_kit/templates/server_cost.html',
                  dict(SERVER=json_parsed_data,))


@admin_extension(title="Cost and Security Management",
                 description="Initial configuration setting")
def display_admin(request, **kwargs):
    """
    To show the Admin tab in Admin section of CMP

    Args:
        request (http request)

    Returns:
        html: renders admin.html file
    """
    _collect_static()
    return render(request, 'kumo_integration_kit/templates/admin.html',
                  context={'docstring': 'Kumolus integration setup'})
