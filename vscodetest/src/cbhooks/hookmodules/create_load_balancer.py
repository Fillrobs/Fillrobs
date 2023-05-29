from django.utils.text import slugify

from common.methods import set_progress
from servicecatalog.models import LoadBalancerServiceItem
from utilities.exceptions import CloudBoltException


def run(job, logger=None):
    params = job.job_parameters.cast()
    resource = job.parent_job.resource_set.first()
    args = params.arguments
    lbsi = None
    if args and "lbsi_id" in args:
        lbsi = LoadBalancerServiceItem.objects.get(id=args["lbsi_id"])

    if lbsi and lbsi.lb_tech:
        kwargs = lbsi.extra_args
        members = []

        # Set lb_name
        lb_name = None
        # lb_name = lbsi.virtual_name_template
        if lb_name:
            # generate name here
            pass
        else:
            names = [slugify(resource.name)] + [
                slugify(t.name) for t in lbsi.servers.all()
            ]
            lb_name = "-".join(names)

        for tier in lbsi.servers.all():
            # Note: LBSIs are currently only allowed in BPs that create resources.
            # We may eventually lift that restriction, then this code will have to change to get
            # the servers from somewhere else (perhaps the job tree).
            members += list(resource.server_set.filter(service_item=tier))

        # arguments use by all LB types
        kwargs["lbsi"] = lbsi
        kwargs["members"] = members
        kwargs["virtual_name"] = lb_name

        # TODO: Grow support fpr more complex port mappings
        kwargs["ports"] = {
            "src_port": "{{ source_port }}",
            "dest_port": "{{ destination_port }}",
        }

        lb = lbsi.lb_tech.construct(resource, **kwargs)
        set_progress("Added load balancer: {}".format(lb.get_url()))
        return "", "", ""

    raise CloudBoltException(
        "The Load Balancer being built doesn't have a technology associated!"
    )
