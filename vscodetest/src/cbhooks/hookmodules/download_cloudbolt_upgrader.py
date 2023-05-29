#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from past.utils import old_div
from utilities.helpers import cb_request
import hashlib
import os
import requests  # noqa: F401
import sys

from django.utils.translation import ugettext as _

if __name__ == "__main__":
    import django

    django.setup()

import settings

from common.methods import get_proxies, set_progress  # noqa: F401
from jobs.models import Job
from utilities.exceptions import ChecksumIncorrect
from utilities.helpers import get_ssl_verification  # noqa: F401
from utilities.models import CBReleaseInfo
from utilities.run_command import execute_command

ONE_MB = 1024 * 1024


def sha256_for_file(f, block_size=ONE_MB):
    """
    :param f: a file object, open for reading
    :param block_size: how many bytes to read at a time (default: 1MB)
    :return: the sha256 digest
    """
    h = hashlib.sha256()
    while True:
        data = f.read(block_size)
        if not data:
            break
        h.update(data)
    return h.hexdigest()


def download_file(url, dst_filename):
    """
    Download the file at `url` to `dst_filename` on the local filesystem.

    Determines the file size before beginning the download and sets progress for the current job
    as it runs so that the progress bar proceeds according to how many bytes been downloaded.
    The progress updates are throttled to only happen every 1 MB that is downloaded.
    """
    # initial code taken from:
    # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests

    # Use a proxy if it's configured
    r = cb_request("GET", url, stream=True)

    # if the HTTP response was not 2xx, raise an exception and go no further
    r.raise_for_status()

    total_size = int(r.headers["content-length"])
    total_size_mb = old_div(total_size, ONE_MB)
    set_progress("Beginning download of {} MB upgrader".format(total_size_mb))
    bytes_saved = 0
    set_progress(total_tasks=total_size)
    previous_prog_update_bytes = 0
    with open(dst_filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            bytes_saved += len(chunk)
            # Update the progress every 1 MB
            if bytes_saved > previous_prog_update_bytes + ONE_MB:
                set_progress(tasks_done=bytes_saved)
                previous_prog_update_bytes = bytes_saved
    set_progress(tasks_done=total_size)


def get_args(job):
    """
    Given a job, extract and return a tuple with the parameters: (URL, destination directory,
    destination filename)
    """
    params = job.job_parameters.cast()
    release_info_id = params.arguments["release_info_id"]
    upgrade = params.arguments.get("upgrade", False)

    rel_info = CBReleaseInfo.objects.get(id=release_info_id)
    url = rel_info.upgrader_url

    upgrader_filename = url.rsplit("/", 1)[-1]
    dst_path = "/var/tmp"
    dst_filename = os.path.join(dst_path, upgrader_filename)
    return rel_info, url, dst_path, dst_filename, upgrade, upgrader_filename


def verify_checksum(filepath, rel_info):
    """
    Compare the checksum of the file at filepath to the one stored in the rel_info.

    Raise ChecksumIncorrect on failure, otherwise return None.
    """
    set_progress("Computing checksum for downloaded file ({})".format(filepath))
    with open(filepath, "rb") as f:
        computed_checksum = sha256_for_file(f)
    if computed_checksum != rel_info.checksum:
        set_progress("Checksum verification failed, deleting the downloaded file.")
        os.unlink(filepath)
        raise ChecksumIncorrect(
            "The computed checksum ({}) did not match the expected checksum "
            "({}).".format(computed_checksum, rel_info.checksum)
        )
    set_progress("Checksum verified")


def untar_upgrader(dst_path, upgrader_filename):
    os.chdir(dst_path)
    cmd = f"tar xfz {upgrader_filename}"
    execute_command(cmd, stream_title="Unpacking the upgrader")
    upgrader_path = os.path.join(dst_path, upgrader_filename)
    # strip the trailing '.tgz' off of the upgrader filename and it should be the name of the directory that the
    # upgrader lives in
    upgrader_path, _ = upgrader_path.rsplit(".", 1)
    return upgrader_path


def run_upgrader(upgrader_path):
    os.chdir(upgrader_path)
    cmd = "./upgrade_cloudbolt.sh -e"
    stdout_file = os.path.join(settings.TMP_DIR, "cloudbolt_upgrader_job_stdout.log")
    stderr_file = os.path.join(settings.TMP_DIR, "cloudbolt_upgrader_job_stderr.log")
    proc = execute_command(
        cmd,
        stream_title="Initiating the upgrade",
        run_synchronously=False,
        stdout_file=stdout_file,
        stderr_file=stderr_file,
    )
    return proc


def run(**kwargs):
    """
    Download a file at a given URL to the CB filesystem
    """
    msg = ""
    job = kwargs.get("job")
    rel_info, url, dst_path, dst_filename, upgrade, upgrader_filename = get_args(job)

    if os.path.isfile(dst_filename):
        msg = (
            "File already exists at destination path {}, perhaps it was already "
            "downloaded".format(dst_filename)
        )
    else:
        set_progress("Downloading {} to {}".format(url, dst_path))
        download_file(url, dst_filename)
        msg = "Download completed successfully."
        set_progress(msg)
    verify_checksum(dst_filename, rel_info)

    if upgrade:
        if getattr(settings, "UPGRADER_OVERRIDE_PATH", ""):
            # This setting is available for CB testing, so we can test upgrades from the UI to a development version,
            # rather than the latest GA/RC/alpha. This is important for testing changes to the feature of upgrading from
            # the UI, to avoid downgrading while we are testing and ensure that any features the upgrader needs to
            # support upgrades (ex. email notifications) from the UI are present in the upgrader we are running.
            set_progress(
                f"settings.UPGRADER_OVERRIDE_PATH of {settings.UPGRADER_OVERRIDE_PATH} detected. Will run the "
                "upgrader in this directory instead of using the downloaded upgrader."
            )
            run_upgrader(settings.UPGRADER_OVERRIDE_PATH)
        else:
            upgrader_path = untar_upgrader(dst_path, upgrader_filename)
            run_upgrader(upgrader_path)
        msg = _(
            "The upgrader is now running. This page will be inaccessible when the system enters "
            "maintenance mode, but the version and upgrade info page will show the progress of the upgrade. "
            "Check back soon, or check the logs in /var/log/cloudbolt/install/"
        )

    return "SUCCESS", msg, ""


if __name__ == "__main__":
    # Useful for testing purposes
    print(run(job=Job.objects.get(id=sys.argv[1])))
