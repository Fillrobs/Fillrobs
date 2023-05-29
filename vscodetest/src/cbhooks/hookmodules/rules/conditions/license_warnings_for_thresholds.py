from product_license.license_service import LicenseService


DAY_THRESHOLD = int("{{ threshold_days_before_expires }}")
SVR_THRESHOLD = int("{{ threshold_percent_servers_used }}")


def check(job, logger):
    job.set_progress(
        "Examining license to see if it expires in "
        "less than {} days or more than {}% of its "
        "maximum possible servers are in use".format(DAY_THRESHOLD, SVR_THRESHOLD)
    )
    warnings = LicenseService().get_license_warnings(DAY_THRESHOLD, SVR_THRESHOLD)

    if warnings:
        job.set_progress("Found license warnings")
        return (
            "SUCCESS",
            "",
            "",
            {"slug": "license-warning", "context": {"warnings": warnings}},
        )

    return ("SUCCESS", "", "", None)
