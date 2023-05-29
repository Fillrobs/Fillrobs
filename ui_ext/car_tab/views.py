"""
Module contains all views for this extension package.
"""
import json
from django.shortcuts import render

from extensions.views import tab_extension, TabExtensionDelegate
from resources.models import Resource

from . import car_tab_helpers

car_tab_helpers.create_car_info_parameters_if_needed()


#
# All of these delegates only display their tab if the server object has the relevant OS info.
#
class CarOptionsInfoTabDelegate(TabExtensionDelegate):
    def should_display(self):
        # Handle when attr is not defined and when it's empty
        val = getattr(self.instance, "car_options", None) or None
        return val is not None


@tab_extension(model=Resource, title="Car Options", delegate=CarOptionsInfoTabDelegate)
def car_options_tab(request, obj_id):
    """
    This extension adds an "Car Options" tab to Cars so that you can view
    a list of options available to a car, e.g. Spoiler or Go fast stripes.
    """

    show_table = True
    car = Resource.objects.filter(resource_type__name="car", id=obj_id).first()
    rows = []
    jsonObject = json.loads(car.car_options)

    for x in jsonObject:
        rows.append(
            "<td>"
            + x["Name"]
            + "</td><td>"
            + x["DisplayName"]
            + "</td><td>"
            + x["State"]
            + "</td><td>"
            + x["OptionSize"]
            + "</td>",
        )

    return render(
        request,
        "car_tab/templates/table.html",
        dict(
            show_table=show_table,
            pagetitle="Car Options",
            table_caption="Showing options for {}".format(car.name),
            column_headings=["Option Name", "Option Label", "Status", "Option Size"],
            rows=rows,
            sort_by_column=1,
            unsortable_column_indices=[],
        ),
    )
