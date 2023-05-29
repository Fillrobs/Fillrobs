from __future__ import print_function
import json
import os
import sys
import time
import zipfile


def update_pythonpath():
    """
    Updates sys.path so that the required modules can be imported, regardless
    of whether the user's PYTHONPATH is set or what it is set to.

    The sample API scripts all need to be able to import client.py, requests,
    and argparse. This method should be called by the sample scripts before any
    of those are imported and it will add the script's grandparent dir to the
    path.

    Assumes that this module is in a location like:
        samples/api_helpers.py
        where samples has a sibling dir named ext/

    After calling this method, scripts can do things like:
        from api_client import CloudBoltAPIClient
        from ext import argparse

    Returns None.
    """
    samples_dir = os.path.abspath(os.path.dirname(__file__))
    api_rootdir = os.path.dirname(samples_dir)  # this is the python_client dir
    ext_dir = os.path.join(api_rootdir, "ext")
    # add the API directory as the first one in the pythonpath so we know when
    # we import modules we are getting the ones we want
    sys.path.insert(0, ext_dir)
    sys.path.insert(0, api_rootdir)


def create_order_for_group(cb, group_id, owner_id=None):
    """
    Starts a new order for this group on the cb connection, where the Group ID can be either
    its Global ID (recommended) or primary key ID.
    Optionally sets the owner to the User with ID=owner_id.
    """
    print("Creating order for group {0}...".format(group_id))
    body = {"group": "/api/v2/groups/{0}".format(group_id)}

    if owner_id:
        body["owner"] = "/api/v2/users/{0}".format(owner_id)
        print("... and owner {0}".format(owner_id))
    raw_response = cb.post("/api/v2/orders/", json.dumps(body))

    response = json.loads(raw_response)
    if "status_code" in response and not 200 <= response["status_code"] < 300:
        error = pretty_print(response)
        print("Error creating order through the API: {0}".format(error))
        sys.exit(1)

    order_url = response["_links"]["self"]["href"]
    order_id = order_url.replace("/api/v2/orders/", "").strip("/")

    print("Order {order_id} created.".format(order_id=order_id))
    return int(order_id)


def pretty_print(dictionary):
    """
    Method to print out the entire response dict in a nice way
    """
    pp = ""
    for key in list(dictionary.keys()):
        pp += "{0}: {1}\n".format(key, dictionary[key])
    return pp


def get_order(cb, order_id):
    """
    Return dict representing an order details JSON.
    """
    return json.loads(cb.get("/api/v2/orders/{0}/".format(order_id)))


def submit_order(cb, order_id):
    """
    Submit order for approval.
    """
    print("Submitting order {0}...".format(order_id))
    response = json.loads(cb.post("/api/v2/orders/{0}/actions/submit".format(order_id)))
    print("Response:\n", response)
    return response


def approve_order(cb, order_id):
    """
    Approve order.
    """
    print("Approving order {0}...".format(order_id))
    response = json.loads(
        cb.post("/api/v2/orders/{0}/actions/approve".format(order_id))
    )
    print("Response:\n", response)
    return response


def wait_for_order_completion(cb, order_id, timeout_sec, interval_sec):
    """
    Polls CB for this order's status to change from 'ACTIVE', retrying every
    interval_sec seconds.

    When complete, prints the output & error fields from each job in the order.

    If the order suceeds, return 0.  If the order fails, return 1, if the wait
    timeout is reached, return 3.
    """
    print("Waiting for order to complete (timeout {0}s)...".format(timeout_sec))
    order = get_order(cb, order_id)

    start = time.time()
    waited = 0
    completed = ["SUCCESS", "WARNING", "FAILURE"]
    while waited < timeout_sec and order["status"] not in completed:
        time.sleep(interval_sec)
        waited = time.time() - start
        order = get_order(cb, order_id)
        sys.stdout.write(".")
        sys.stdout.flush()

    print("\n")
    if waited >= timeout_sec:
        # By returning this instead of printing, the caller can send it
        # to stderr instead (via sys.exit() for example).
        print(
            "Failed: Order did not complete within {0}s. "
            "Most recent order status was {1}.".format(timeout_sec, order["status"])
        )
        return 3

    print_order_job_outputs(cb, order)
    if order["status"] != "SUCCESS":
        return 1
    return 0


def wait_for_job_completion(cb, job_id, timeout_sec, interval_sec):
    """
    Polls CB for this job's status to change to a completed one, retrying every
    interval_sec seconds.

    When complete, prints the output & error fields from the job.

    If the job suceeds, return 0.  If the job fails, return 1, if the wait
    timeout is reached, return 3.
    """
    print("Waiting for job to complete (timeout {0}s)...".format(timeout_sec))
    job = json.loads(cb.get("/api/v2/jobs/{}/".format(job_id)))

    start = time.time()
    waited = 0
    completed = ["SUCCESS", "WARNING", "FAILURE", "CANCELED"]
    while waited < timeout_sec and job["status"] not in completed:
        time.sleep(interval_sec)
        waited = time.time() - start
        job = json.loads(cb.get("/api/v2/jobs/{}/".format(job_id)))
        sys.stdout.write(".")
        sys.stdout.flush()

    print("\n")
    if waited >= timeout_sec:
        # By returning this instead of printing, the caller can send it
        # to stderr instead (via sys.exit() for example).
        print(
            "Failed: Job did not complete within {0}s. "
            "Most recent job status was {1}.".format(timeout_sec, job["status"])
        )
        return 3

    print(job["_links"]["self"]["title"])
    print("Output: ", job.get("output", "no output"))
    print("Errors: ", job.get("errors", "no errors"))
    if job["status"] != "SUCCESS":
        return 1
    return 0


def print_order_job_outputs(cb, order):
    """
    Prints the output & error for each job within this order
    """
    for j in order["_links"]["jobs"]:
        job = json.loads(cb.get(j["href"]))
        print(job["_links"]["self"]["title"])
        print("Output: ", job.get("output", "no output"))
        print("Errors: ", job.get("errors", "no errors"))


def zipdir(dir_path=None, zip_path=None, include_dir_in_zip=True):
    """
    Zips up `dir_path` and returns the zip file's path.

    `dir_path` may be '~/a/b/dirname' or '/c/d/dirname' or 'e/f/dirname'.

    `zip_path`: optional path for the new zip file.  By default the zip file is
    created next to the directory and named after it.

    `include_dir_in_zip`: if True (default), the archive will have one base
    directory named after the directory being zipped; otherwise no prefix will
    be added to the archive members.

    E.g.
        zip_dir('~/a/b/dirname')
          -> dirname.zip with files like 'dirname/blueprint.json'
    """
    dir_path = dir_path.rstrip("/")
    dir_path = os.path.abspath(os.path.expanduser(dir_path))

    if not zip_path:
        zip_path = dir_path + ".zip"
    if not os.path.isdir(dir_path):
        raise OSError(
            "dir_path argument must point to a directory. " "'%s' does not." % dir_path
        )
    parent_dir, dir_to_zip = os.path.split(dir_path)

    # Little nested function to prepare the proper archive path
    def trimPath(path):
        archive_path = path.replace(parent_dir, "", 1)
        if parent_dir:
            archive_path = archive_path.replace(os.path.sep, "", 1)
        if not include_dir_in_zip:
            archive_path = archive_path.replace(dir_to_zip + os.path.sep, "", 1)
        return os.path.normcase(archive_path)

    out_file = zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED)
    for (archive_path, dir_names, file_names) in os.walk(dir_path):
        for fileName in file_names:
            filePath = os.path.join(archive_path, fileName)
            out_file.write(filePath, trimPath(filePath))
    out_file.close()
    return zip_path


update_pythonpath()
from ext import argparse


class BaseAPIArgParser(object):
    def parse(self):
        parser = argparse.ArgumentParser(prog=sys.argv[0])

        parser.add_argument(
            "--username", help="CB username to authenticate as", required=True
        )
        parser.add_argument("--password", help="CB user password", required=True)
        parser.add_argument(
            "--token", help="CB user 2-factor authentication token", required=False
        )
        parser.add_argument("--domain", help="CB user AD/LDAP doamin", required=False)
        parser.add_argument(
            "--host", help="CB server host or IP address", required=True
        )
        parser.add_argument("--port", help="CB server port", default="443")
        parser.add_argument(
            "--protocol", help="Optional CB server protocol", default="https"
        )
        parser.add_argument(
            "--verify",
            help="Optional boolean whether the SSL cert will be verified",
            dest="verify",
            action="store_true",
        )
        parser.add_argument(
            "--cert", help="Optional path to ssl client cert file", default=None
        )
        self.add_arguments(parser)

        return parser.parse_args(sys.argv[1:])

    def add_arguments(self, parser):
        pass  # to be optionally defined in subclasses

    def parameter_kwarg_strings_to_dict(self, strings):
        """
        Convert ["name1=val1", "name2=val2"]
             to {'name1': 'val1', 'name2': 'val2'}
        """
        if not strings:
            return {}
        params = {}
        for kv in strings:
            key, value = kv.split("=")
            params[key] = value
        return params
