"""
Module contains all views for this extension package.
"""
import datetime

from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from accounts.models import Group
from common.methods import last_month_day_info, get_rh_html_display
from extensions.views import report_extension
from infrastructure.models import Environment
from utilities.permissions import cbadmin_required
from utilities.templatetags import helper_tags
from infrastructure.templatetags import infrastructure_tags

from .forms import DateRangeForm

# lex
from orders.models import Order
from jobs.models import Job
from reportengines.internal.forms import (
    InternalReportExportForm,
    CostReportForm,
    CustomServerReportColumnsForm,
    CustomServerReportFilterForm,
    CustomServerReportFilterFormset,
    ReportEmailForm,
    GroupCostDetailReportColumnsForm,
)


# To install your own custom thumbnail image, say "pie_chart.png":
#
# 1. scp image file to /var/www/html/cloudbolt/static/uploads/extensions/pie_chart.png
# 2. run `/opt/cloudbolt/manage.py collectstatic --noinput`
# 3. change the decorator line below to this:
#     @report_extension(title='...', thumbnail='pie_chart.png')


@report_extension(title="Test Report")
def cdr_billing_report(request):
    """
    Draw a date range form and once it is posted include a tabular report.

    """
    profile = request.get_user_profile()
    if not profile.super_admin:
        raise PermissionDenied("Only super admins can view this report.")

    # Default date range from 1st to last day of last month, without time part
    start, end = last_month_day_info()
    start = start.date()
    end = end.date()

    # Hide table until form has been submitted
    show_table = False

    column_headings = [
        "Account Number",  # preconf
        "Event Source",  # order
        "Event Date",  # order date
        "Event Duration",
        "Entity Name",  # hostname
        "Resourse ID",
        "Amount",
        "Service Name",
    ]

    rows = []

    if request.method == "GET":
        form = DateRangeForm(initial=dict(start_date=start, end_date=end))
    else:
        show_table = True

        form = DateRangeForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data["start_date"]
            end = form.cleaned_data["end_date"]
            #############################################################################################
            for job in Job.objects.filter(
                type="provision", created_date__range=(start, end)
            ):
                account_number = "E000039207"
                event_source = job.get_order()  # TODO
                event_date = job.start_date
                event_duration = job.get_seconds_to_complete()
                entity_name = job.server_set.last()
                res_id = 5  # TODO
                amount = 100 * event_duration  # TODO time by rate
                service_name = "NeoCloud Usage"
                # Each row is a tuple of cell values
                rows.append(
                    (
                        account_number,
                        event_source,
                        event_date,
                        event_duration,
                        entity_name,
                        res_id,
                        amount,
                        service_name,
                    )
                )
        else:
            # form will be re-rendered with validation errors
            pass

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
        "report_extensions/templates/special.html",
        dict(
            pagetitle="CUSTOM REPORT",
            report_slug="Custom ",
            intro="""
            Sample report extension.
            """,
            export_form=InternalReportExportForm(report="cdr_billing_report"),
            show_table=show_table,
            table_caption="Shows servers added between {} and {}".format(start, end),
            form=form,
            column_headings=column_headings,
            rows=rows,
            # numeric column index (0-based) to sort by
            sort_by_column=2,
            # numeric column index (0-based) where sort is disabled
            unsortable_column_indices=[],
        ),
    )
