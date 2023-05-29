"""
Functions used by car_tabcar.views
"""
import json
from infrastructure.models import CustomField
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def create_car_info_parameters_if_needed():
    """
    This UI extension is smart enough to create the CFs it needs. Six fewer steps for admins to do.
    """
    params = [
        [
            "car_options",
            "Car Options",
            "Additional Car Options",
        ],
    ]

    for name, label, desc in params:
        cf, created = CustomField.objects.get_or_create(name=name)
        if created:
            cf.label = label
            cf.description = desc
            cf.type = "CODE"
            cf.save()

            logger.info(
                "Created new parameter {} for the Car Tab UI extension.".format(name)
            )


def render_table(caption, data, fields, lookup_functions=None):
    rows = []
    data = json.loads(data, strict=False)
    for row in data:
        _row = []
        for field in fields:
            col = row.get(field, "")
            if lookup_functions and field in lookup_functions:
                col = lookup_functions[field](col)
            _row.append(col)
        rows.append(_row)
    return {
        "caption": caption,
        "column_headings": fields,
        "rows": rows,
        "sort_by_column": 0,
        "unsortable_column_indices": [],
    }
