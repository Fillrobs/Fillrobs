from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from accounts.models import Group
from common.methods import last_month_day_info
from extensions.views import report_extension
from resources.models import Resource
from utilities.permissions import cbadmin_required
from django.utils.safestring import mark_safe

from .forms import DateRangeForm


def show_image(fn):
    img_file = "/static/uploads/images/car_logos/" + fn + ".JPG"
    dimensions = "width=50px"
    return mark_safe("<img src='{}' {} />".format(img_file, dimensions))


@report_extension(title="Car Stock Report")
def car_table_report(request):
    """
    This shows a list of the Cars in the Custom Resource Type cars

    """
    profile = request.get_user_profile()
    if not profile.super_admin:
        raise PermissionDenied("Only super admins can view this report.")

    # Default date range from 1st to last day of last month, without time part
    start, end = last_month_day_info()
    start = start.date()
    end = end.date()

    # Show table
    show_table = False

    column_headings = [
        "ID",
        "Registration",
        "Manufacturer",
        "Logo",
        "Model",
        "Engine",
        "Colour",
        "Purchased",
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
            carstock = (
                Resource.objects.filter(resource_type__name="car")
                .filter(created__range=[start, end])
                .all()
            )
            # carstock = {"car_id": 1, "name": "abc", "manufid": 1, "car_modelid": 4}

            for car in carstock:
                # Each row is a tuple of cell values
                st = car.get_resource_dict()["status"]
                if st == "ACTIVE":
                    modelid = car.car_modelid
                    car_details = Resource.objects.filter(
                        resource_type__name="car_model", id=modelid
                    ).first()
                    try:
                        car_details_manuf = car_details.manuf
                    except AttributeError:
                        car_details_manuf = "None"

                    try:
                        car_details_name = car_details.name
                    except AttributeError:
                        car_details_name = "None"

                    car_details_logo = car_details_manuf.lower()
                    car_details_logo = car_details_logo.replace(" ", "")

                    car_details_final_logo = show_image(car_details_logo)

                    rows.append(
                        (
                            car.car_id,
                            car.name,
                            car_details_manuf,
                            car_details_final_logo,
                            car_details_name,
                            car.car_engine_size,
                            car.car_colour,
                            car.created,
                        )
                    )

    return render(
        request,
        "reports/table.html",
        dict(
            show_table=show_table,
            form=form,
            pagetitle="Car Stock Report",
            report_slug="Car Stock Report",
            table_caption="Shows Cars added between {} and {}".format(start, end),
            column_headings=column_headings,
            rows=rows,
        ),
    )
