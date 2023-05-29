"""
Recurring job to download the CloudBolt Content Library list view context to the
CloudBolt filesystem. It's meant to speed up visits to the content library page.
"""
import json
import os

from content_library.views import CONTENTLIBRARY_CACHE_LOCATION_PATH
from utilities.cb_http import get_exportable_content


def write_list_to_file(somelist, file_path):
    with open(file_path, "w") as fl:
        json.dump(somelist, fl, indent=4)


def run(*_args, **_kwargs):
    exportable_content = None
    from utilities.models import ConnectionInfo

    ci = ConnectionInfo.objects.filter(name__endswith="Content Library").first()
    if ci:
        exportable_content = get_exportable_content(ci, collection="all")

    for collection, content_list in exportable_content.items():
        if content_list is not None:
            # if the return is an empty list we still want to cache it.  Non means the key was not
            # returned at all
            os.makedirs(CONTENTLIBRARY_CACHE_LOCATION_PATH, exist_ok=True)
            path = os.path.join(
                CONTENTLIBRARY_CACHE_LOCATION_PATH, f"{collection}.json"
            )
            write_list_to_file(content_list, path)
