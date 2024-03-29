# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-13 20:16
from __future__ import unicode_literals

from django.db import migrations


def set_resource_type_on_existing_services(apps, schema_editor):
    """
    At this point all existing Service objects are actual services, not any
    other resource type. They also need to be associated with the 'service'
    ResourceType in order to show up correctly in lists and such.
    """
    ResourceType = apps.get_model('services', 'ResourceType')
    Service = apps.get_model('services', 'Service')
    service_rt = ResourceType.objects.filter(name='service').first()
    if service_rt:
        Service.objects.all().update(resource_type=service_rt)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_service_resource_type'),
    ]

    operations = [
        migrations.RunPython(set_resource_type_on_existing_services),
    ]
