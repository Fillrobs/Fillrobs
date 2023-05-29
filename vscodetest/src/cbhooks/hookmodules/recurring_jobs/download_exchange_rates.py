import os
import shutil
import zipfile

from django.conf import settings

from common.methods import set_progress
from utilities.filesystem import mkdir_p
from utilities.logger import ThreadLogger
from utilities.helpers import cb_request

logger = ThreadLogger(__name__)
EXCHANGE_URL = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip"


def __download_and_unzip_conversion_rates():
    """
    Remove existing exchange rate directory if it exists, and create an empty
    directory for the new file. Then, download the new exchange rate file and
    unzip it.
    """
    directory = f"{settings.VARDIR}opt/cloudbolt/exchange_rates"
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    mkdir_p(directory)

    base_filename = "eurofxref.zip"
    zip_filename = os.path.join(directory, base_filename)

    __download_zip_file(base_filename, zip_filename)
    __unzip_file(base_filename, zip_filename, directory)


def __download_zip_file(base_filename, zip_filename):
    """
    Download a zip file containing an exchange rate csv to the specified
    directory.
    """
    set_progress(f"Downloading file {base_filename} to {zip_filename}.")
    r = cb_request("GET", EXCHANGE_URL, stream=True)
    with open(zip_filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    set_progress("Download complete.")


def __unzip_file(base_filename, zip_filename, directory):
    """
    Unzip the exchange rate csv and then remove the original zip file.
    """
    zip_file = zipfile.ZipFile(zip_filename)
    for name in zip_file.namelist():
        if name.endswith(".csv"):
            logger.info(f"Extracting {name} from {base_filename}")
            zip_file.extract(name, path=directory)
            break
    os.unlink(zip_filename)


def run(*args, **kwds):
    """
    Download the latest currency exchange rates (single day data source) from
    the European Central Bank.
    """
    status = "SUCCESS"
    try:
        __download_and_unzip_conversion_rates()
    except Exception as e:
        msg = f"Failed to get exchange rate data: {e}"
        set_progress(msg)
        logger.exception(msg)
        status = "FAILURE"

    return status, "", ""
