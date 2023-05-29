# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-06 17:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0017_auto_20180201_1841'),
        ('resources',
         '0002_move_services_app_objs_to_resources_app_20180201_1903'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='attributes',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='blueprint',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='group',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='jobs',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='parent_resource',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='resource_type',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetwork',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetwork',
            name='network',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetwork',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetwork',
            name='resource_handler',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetwork',
            name='service_item',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetworkappliance',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetworkappliance',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='softwaredefinednetworkappliance',
            name='resource_handler',
        ),
        migrations.DeleteModel(
            name='Resource',
        ),
        migrations.DeleteModel(
            name='ResourceType',
        ),
        migrations.DeleteModel(
            name='SoftwareDefinedNetwork',
        ),
        migrations.DeleteModel(
            name='SoftwareDefinedNetworkAppliance',
        ),
    ]
