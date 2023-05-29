"""
Methods to populate the data for the form
are stored in this module.
"""
from django.http import HttpResponse
from datetime import datetime, timedelta
from infrastructure.models import Environment
from resourcehandlers.models import ResourceHandler
from accounts.models import UserProfile
from utilities.logger import ThreadLogger

LOGGER = ThreadLogger(__name__)


def generate_options_for_resource_handlers():
    # this shows them all
    rts = ResourceHandler.objects.all()
    # need to get self or requests in here
    #profile = request.get_user_profile()
    
    #five_minutes_ago = datetime.now() - timedelta(minutes=5)
    #current_user_profile = UserProfile.objects.filter(last_activity_time__gte=five_minutes_ago).first()
    
    #envs = Environment.objects_for_profile(current_user_profile)
    #list_of_envs = [env.resource_handler for env in envs if env.resource_handler and env.resource_handler.resource_technology.type_slug in ['aws', 'azure_arm']]
    #rts = set(list_of_envs)
    # only AWS type RH
    options = []
    for r in rts:
        options.append((r.id, r.name))

    options.append((99, 'dummy'))
    return options
