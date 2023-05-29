from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run(job, *args, **kwargs):

    logger.info("schedule_reccurring_job run")

    return "", "", ""
