# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-03 23:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0040_azurearmnodesize'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='azurearmnodesize',
            name='arm_server',
        ),
        migrations.DeleteModel(
            name='AzureARMNodeSize',
        ),
    ]