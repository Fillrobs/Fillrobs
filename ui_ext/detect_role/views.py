
from django.shortcuts import render
from extensions.views import report_extension, ReportExtensionDelegate
from common.methods import set_progress
import requests
import sys

# Maxis
# financeuser group = id 5
# Customer Admin role Id = 12

# Lab
# Phil Robins = id 11
# CustomerA = group id 13
# group admin role id = 5

class detect_role_Delegate(ReportExtensionDelegate):
    def should_display(self):

        can_view = self.viewer.is_super_admin
        if can_view == False:
            profile = request.get_user_profile()
            # to be replaced with code to determine if Customer Admin role is true
            if profile.user_id == 5:
                can_view = True
        return can_view

@report_extension(title="Detect Role", delegate=detect_role_Delegate)
def detect_role(request):
    profile = request.get_user_profile()
    msg = "user profile is {}".format(profile)
    set_progress(msg)
    return render(
        request,
        "detect_role/templates/special.html",
        dict(
            pagetitle="Detect Role",
            profile=profile,
        ),
    )