# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 20:32
from __future__ import unicode_literals

from django.db import migrations


def rename_hook_point(apps, schema_editor):
    """
    In the course of searching for references to "service" to be changed, I
    realized there was a HookPoint named that in cb_minimal. I'm not entirely
    sure if it's still used, but seems to have been intended for use with build
    items in blueprints like load balancers and networks, so changing it to
    represent that. Renaming it here because otherwise create_objects would make
    a new one, but then create_objects can take care of updating the label and
    description.
    """
    HookPoint = apps.get_model("cbhooks", "HookPoint")

    hook_point = HookPoint.objects.filter(name='service').first()
    if hook_point:
        hook_point.name = 'blueprint'
        hook_point.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0032_service_actions_hookpoint_becomes_resource_actions_20180115_1357'),
    ]

    operations = [
        migrations.RunPython(rename_hook_point,
                             migrations.RunPython.noop),
    ]