"""
Refreshes the search index that enables the global search feature. Running this on a
regular basis ensures that objects new to CloudBolt will show up in search results.

The search index resides in /var/opt/cloudbolt/search_index/ and should only take a few
minutes to update.
"""
from six import StringIO
from django.core.management import call_command
from django.conf import settings
import shutil
import os


def run(job, logger=None, *args, **kwds):
    """
    Calls the `update_index` Django management command.
    """
    try:
        output = StringIO()
        call_command("update_index", stdout=output)
        job.set_progress(
            "Successfully ran django management command: update_index", logger=logger
        )
    except TypeError:
        # a TypeError occurs when the search index is corrupted.
        # best route to take here is to remove the current search index and rebuild it.
        job.set_progress(
            "The search index is corrupt. Will remove the existing index and build a new one.",
            logger=logger,
        )
        # instantiate a new StringIO object to avoid concatenation of the previous output.
        output = StringIO()

        # remove the entire search_index directory
        filepath = os.path.join(settings.VARDIR, "opt/cloudbolt/search_index")
        shutil.rmtree(filepath)

        job.set_progress("Re-building the index...", logger=logger)
        # rerun update_index to build a new one
        call_command("update_index", stdout=output)

    return "SUCCESS", output.getvalue(), ""


if __name__ == "__main__":
    """
    For testing, call this directly like so:
        python update_search_indexes.py
    """
    import django

    django.setup()
    run()
