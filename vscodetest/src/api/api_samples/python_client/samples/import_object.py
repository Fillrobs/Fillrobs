#!/usr/bin/env python
"""
Script uses the CB REST API to import an object from the filesystem.

    import_object.py \
        --username user --password passw [--token token] [--domain domain] \
        --host cb-ip-or-host  --port port --protocol http \
        --collection blueprints --zip-file ~/Downlaods/action.zip
        [--replace-existing]
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import sys

# Add samples directory to path so we can import api_helpers
samples_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, samples_dir)

from api_helpers import update_pythonpath, zipdir, BaseAPIArgParser

update_pythonpath()

from api_client import CloudBoltAPIClient


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.
        parser.add_argument(
            "--collection",
            required=True,
            help='Collection of the new object (e.g., "actions", '
            '"blueprints", "server-actions", "rules", etc)',
        )
        parser.add_argument(
            "--zip-file",
            required=False,
            help="Path to a Zip file of the format produced by "
            "exporting an object (must contain at least a "
            ".json file)",
        )
        parser.add_argument(
            "--dir",
            required=False,
            help="Path to a directory that contains the object "
            "JSON file and any associated files.",
        )
        parser.add_argument(
            "--replace-existing",
            action="store_true",
            help="""
                            Replace existing objects that match by name.  By
                            default, import creates new objects (assigning unique
                            names where needed) and leaves existing objects alone.

                            When importing blueprints, this applies not only to the
                            blueprint but to any actions used by it.
                            """,
        )


def import_object(cb, file_name, collection, replace_existing=False):
    """
    Post the Zip archive to the specified collection to import it.
    """
    files = {"file": (file_name, open(file_name, "rb"))}

    url = "v2/{collection}/import/".format(collection=collection)
    if replace_existing:
        url += "?replace-existing=1"

    response = cb.post(url, files=files)
    print("Response:")
    print(response)


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    if args.dir:
        print("Creating zip archive for dir {directory}...".format(directory=args.dir))
        zip_file = zipdir(args.dir)
    else:
        zip_file = args.zip_file

    import_object(cb, zip_file, args.collection, args.replace_existing)
