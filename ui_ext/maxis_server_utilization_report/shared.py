from datetime import datetime, timedelta

from accounts.models import UserProfile
from orders.models import Group
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def generate_options_for_maxis_customer(profile_id):
    supuser_status = False
    usr = UserProfile.objects.get(id=profile_id)
    options = []
    if usr.is_super_admin:
        supuser_status = True
        grps = Group.objects.all()
        for g in grps:
            options.append((g.id, g.name))
    else:
        # get user groups
        grps = Group.objects.all()
        for g in grps:
            mem = g.get_active_members()
            for m in mem:
                if m.id == profile_id:
                    options.append((g.id, g.name))
    return options
