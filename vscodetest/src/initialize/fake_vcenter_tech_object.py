#!/usr/bin/env python
# Can be passed to create_objects.py manually to create this tech option for testing CB prov job
# scalability

fake_vsphere_restech = {}
fake_vsphere_restech["name"] = "VMware vCenter Simulated"
fake_vsphere_restech["version"] = "6.7"
fake_vsphere_restech["module"] = "resourcehandlers.vmware.fake_vmware_41"


all_resource_technologies = [fake_vsphere_restech]
