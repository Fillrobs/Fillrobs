import json
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from extensions.views import tab_extension, TabExtensionDelegate
from infrastructure.models import Server, CustomField
from orders.models import CustomFieldValue
from resourcehandlers.vmware.models import VsphereResourceHandler


class RecTabDelegate(TabExtensionDelegate):
    def should_display(self):
        rh = self.instance.resource_handler
        if rh:
            rh = rh.cast()
        if isinstance(rh, VsphereResourceHandler):
            return True
        return False


@tab_extension(
    model=Server,
    title="Rec Scheduler",
    description="Rec Schedule Tab",
    delegate=RecTabDelegate,
)
def create_recurring_job(request, obj_id=None):
    cf = CustomField.objects.filter(name="rec_schedule").first()
    if not cf:
        from .rec_utilities import setup_rec_schedule

        setup_rec_schedule()

    server = get_object_or_404(Server, pk=obj_id)
    pretty_schedule = None
    schedule = None
    snapshots = None
    work_order = None
    name = None
    pretty_decom = None
    decom = None
    decom_name = None

    return render(
        request,
        "create_recurring_job/templates/recurring_job_tab.html",
        dict(
            server=server,
            schedule=schedule,
            pretty_schedule=pretty_schedule,
            snapshots=snapshots,
            name=name,
            work_order=work_order,
            decom=decom,
            decom_name=decom_name,
            pretty_decom=pretty_decom,
        ),
    )
