#!/usr/bin/env python

from __future__ import print_function

if __name__ == "__main__":
    import django

    django.setup()

from common.methods import store_info_on_releases, fetch_info_on_releases


def check(job, logger):
    """
    Fetch info on all GA, Alpha, and RC releases currently available and pass on to the action
    to store the info.
    """
    info_on_releases = fetch_info_on_releases()
    logger.info("Info on releases = {}".format(info_on_releases))
    releases = store_info_on_releases(info_on_releases)

    # Filter out releases that are older or of a release type that they have not chosen to
    # check before returning that info. Only newer, relevant releases should trigger the effect
    # action(s).
    releases = [release for release in releases if release.is_relevant()]
    if not releases:
        # no new releases, do not run the action
        return "SUCCESS", "", "", ""

    # TODO: somehow store whether we have already emailed them about this release and don't do it
    #  again
    # TODO: find the most relevant one, not just the first (ex. GA over alpha)
    newest_release = releases[0]
    subject = "A new CloudBolt release is available"
    body = (
        "A new {} release of CloudBolt ({}) is available. Visit the CB admin page for more "
        "info.".format(newest_release.type, newest_release.version)
    )
    context = {
        "subject": subject,
        "message": body,
    }
    # Return the dict to be processed by the "Then" action
    return "SUCCESS", "", "", {"context": context}


if __name__ == "__main__":
    print(check(None, None))
