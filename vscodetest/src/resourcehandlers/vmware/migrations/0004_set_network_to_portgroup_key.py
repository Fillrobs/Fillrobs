# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_network_to_portgroup_key(apps, schema_editor):
    """
    For VMware networks that have a port group key, change their `network`
    attribute from the port group name (which is not unique) to the port group
    key (which is a UUID).
    """
    VmwareNetwork = apps.get_model('vmware', 'VmwareNetwork')
    nets = VmwareNetwork.objects.all()
    for net in nets:
        if net.portgroup_key:
            net.network = net.portgroup_key
            net.save()


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0003_auto_20161004_2121'),
    ]

    operations = [
        migrations.RunPython(set_network_to_portgroup_key),
    ]
