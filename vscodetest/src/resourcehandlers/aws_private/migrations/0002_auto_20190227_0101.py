# -*- coding: utf-8 -*
# Generated by Django 1.11.16 on 2019-02-27 01:01
from __future__ import unicode_literals

from django.db import migrations


def set_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ResourceHandler = apps.get_model('resourcehandlers', 'ResourceHandler')
    private_content_type = ContentType.objects.filter(model='awsprivatehandler').first()
    public_content_type = ContentType.objects.filter(model='awshandler').first()

    for rh in ResourceHandler.objects.all():
        if rh.real_type == private_content_type:
            rh.real_type = public_content_type
            rh.save()

def remove_eucalyptus(apps, schema_editor):
    ResourceTechnology = apps.get_model('resourcehandlers', 'ResourceTechnology')
    try:
        euc = ResourceTechnology.objects.get(slug='eucalyptus')
        euc.delete()
    except ResourceTechnology.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('networks', '0005_auto_20180202_1944'),
        ('infrastructure', '0038_auto_20180625_2145'),
        ('costs', '0008_auto_20190206_0008'),
        ('externalcontent', '0012_duplicate_osbas_in_multiple_rhs'),
        ('history', '0014_auto_20190111_0124'),
        ('resources', '0008_fontawesome_4to5'),
        ('jobs', '0031_recurringjob_last_run'),
        ('resourcehandlers', '0011_resourcehandler_enable_terminal_feature'),
        ('tags', '0006_cloudbolttag_sequence'),
        ('behavior_mapping', '0009_auto_20180119_1931'),
        ('aws_private', '0001_initial_squashed_0002_auto_20170425_2245'),
    ]

    operations = [
        migrations.RunPython(set_content_type),
        migrations.RunPython(remove_eucalyptus),
    ]
