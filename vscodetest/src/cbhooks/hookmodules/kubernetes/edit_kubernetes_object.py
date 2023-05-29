from containerorchestrators.kuberneteshandler.models import KubernetesObject
from utilities.events import add_resource_event
from utilities.exceptions import CloudBoltException


def run(job=None, logger=None, kubernetes_object_id=None, yaml="", **kwargs):
    kube_obj = KubernetesObject.objects.get(id=kubernetes_object_id)
    # Previous YAML can be fetched if you want to use it:
    # old_yaml = kube_obj.get_yaml()
    try:
        cluster = kube_obj.container_orchestrator.cast()
        cluster.edit_container_object(kube_obj, yaml)

        if kube_obj.resource:
            add_resource_event(
                event_type="MODIFICATION",
                resource=kube_obj.resource,
                message="Modified Kubernetes {kind} {name}".format(
                    kind=kube_obj.kind, name=kube_obj.name
                ),
                profile=job.owner,
            )
    except CloudBoltException as e:
        return "FAILURE", "", str(e)
