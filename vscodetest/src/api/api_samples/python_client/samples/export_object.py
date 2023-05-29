#!/usr/bin/env python

"""
Script uses the CB REST API to export an object like an action or blueprint.

If the export succeeds, the downloaded Zip file is written to the current
working directory.

    export_object.py \
        --username user --password passw [--token token] [--domain domain] \
        --host cb-ip-or-host  --port port --protocol http \
        --collection blueprints --obj-id 20
        [--instance-info]
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import sys

# Add samples directory to path so we can import api_helpers
samples_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, samples_dir)

from api_helpers import update_pythonpath, BaseAPIArgParser

update_pythonpath()

from api_client import CloudBoltAPIClient


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.
        parser.add_argument(
            "--collection",
            required=True,
            help='Collection name. Like "actions", '
            '"blueprints", "server-actions", resource-actions", rules", etc.',
        )
        parser.add_argument(
            "--obj-id", required=True, help="ID of the object to be exported"
        )
        parser.add_argument(
            "--instance-info",
            action="store_true",
            default=False,
            help="Include CloudBolt instance specific information such as groups and environments.",
        )


def extract_attachment_filename(response):
    """
    Determine the suggested download file name from the 'content-disposition'
    header which looks like "attachment; filename=Ping Test.zip".

    Return None if the header value cannot be parsed.
    """
    content_disp = response.headers.get("content-disposition")
    if content_disp:
        parts = content_disp.split("=")
        if len(parts) > 1:
            return parts[1].strip()


def export_object(cb, collection, obj_id, include_instance_info):
    url = "v2/{0}/{1}/export/".format(collection, obj_id)
    if include_instance_info:
        url += "?instance-specific-info=1"

    print(
        'Exporting object ID {obj_id} from collection "{collection}"...'.format(
            obj_id=obj_id, collection=collection
        )
    )
    response = cb.get_raw(url)
    # print('Response headers: {}'.format(response.headers))

    if response.status_code == 200:
        # Otherwise give it a unique name by default
        zip_file_name = extract_attachment_filename(
            response
        ) or "export-object-{obj_id}.zip".format(obj_id=obj_id)

        # Write the response to a file
        with open(zip_file_name, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        print("Saved to file: {filename}".format(filename=zip_file_name))
        return zip_file_name
    else:
        raise Exception(
            'Response status code "{status_code}" indicates that something went '
            "wrong.\nResponse: \n{content}".format(
                status_code=response.status_code, content=response.content
            )
        )


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    try:
        export_object(cb, args.collection, args.obj_id, args.instance_info)
    except Exception as ex:
        sys.exit(ex.args[0])
