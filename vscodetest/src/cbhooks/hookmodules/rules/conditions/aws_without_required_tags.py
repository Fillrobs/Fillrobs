from resourcehandlers.aws.models import EC2ServerInfo

REQUIRED_TAGS = ["Name", "Annotation", "Rate_category"]


def check(job, logger):
    """
    Rule that looks for any AWS instances that are lacking
    the required tags listed in the REQUIRED_TAGS variable at the top
    """
    violators = []
    # Get all the EC2ServerInfo objects, which contain tags for AWS instances
    info_objects = EC2ServerInfo.objects.filter(
        server__status__in=["ACTIVE"]
    ).select_related("server")

    # Check each for the required tags, add to violators if missing any
    for info_object in info_objects:
        job.set_progress("Examining server {}".format(info_object.server.hostname))
        tags = info_object.tags  # dictionary
        missing_tags = []
        for tag_name in REQUIRED_TAGS:
            if not tags.get(tag_name):
                missing_tags.append(tag_name)
        if len(missing_tags) > 0:
            job.set_progress(
                "Including server {} because of {} missing tag(s).".format(
                    info_object.server.hostname, len(missing_tags)
                )
            )
            violator = {"server": info_object.server_id, "missing_tags": missing_tags}
            violators.append(violator)

    if len(violators) > 0:
        job.set_progress("Found instancess missing required tags.")
        return ("SUCCESS", "", "", {"type": "Server", "violators": violators})

    return ("SUCCESS", "", "", None)
