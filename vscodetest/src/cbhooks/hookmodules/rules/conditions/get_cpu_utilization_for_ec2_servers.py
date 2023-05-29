from datetime import datetime, timedelta
import boto.ec2.cloudwatch

from resourcehandlers.aws.models import AWSHandler


def get_cpu_utilization(servers):
    """
    This method is a sample of how CPU utilization can be checked, using EC2's cloud watch to
    gather statistics. This could be changed to gather stats from a monitoring system, VMware,
    or even running remote scripts on servers to fetch their load averages.

    :param servers: servers whose CPU stats should be fetched
    :return: an average CPU utilization on those servers
    """
    instance_ids = [server.resource_handler_svr_id for server in servers]
    aws = AWSHandler.objects.first()
    cloudwatch = boto.ec2.cloudwatch.connect_to_region(
        region_name="us-west-2",
        aws_access_key_id=aws.serviceaccount,
        aws_secret_access_key=aws.servicepasswd,
    )
    end = datetime.utcnow()
    start = end - timedelta(minutes=5)
    data_points = cloudwatch.get_metric_statistics(
        60,
        start,
        end,
        "CPUUtilization",
        "AWS/EC2",
        "Average",
        dimensions={"InstanceId": instance_ids},
    )

    if data_points:
        return data_points[-1]["Average"]
    return None
