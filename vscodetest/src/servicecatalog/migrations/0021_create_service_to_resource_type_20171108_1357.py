# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-08 13:57
from __future__ import unicode_literals

from django.db import migrations


def convert_create_service_to_resource_type(apps, schema_editor):
    """
    Examines existing Blueprint objects to see what they have set for the old
    boolean create_service attribute (which will go away in the next migration)
    and properly sets the new resource_type FK so they will continue to behave
    the same way. Uses the new OOTB "Service" RT created by the services' app's
    0005 migration when create_service was True.
    """
    ServiceBlueprint = apps.get_model('servicecatalog', 'ServiceBlueprint')
    ResourceType = apps.get_model('services', 'ResourceType')

    service_rt = ResourceType.objects.get(name='service')
    for bp in ServiceBlueprint.objects.filter(create_service=True):
        bp.resource_type = service_rt
        bp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0020_serviceblueprint_resource_type'),
        ('services', '0005_ootb_service_resourcetype_20171108_1347'),
    ]

    operations = [
        migrations.RunPython(convert_create_service_to_resource_type),
    ]
