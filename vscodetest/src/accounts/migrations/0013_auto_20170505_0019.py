# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 00:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_create_job_owners_without_logs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='allow_auto_approval',
            field=models.BooleanField(default=False, help_text='Approve all orders for this group automatically. If not set, only orders for super admins and users with the order.approve permission will be auto approved.', verbose_name='Auto approve all orders'),
        ),
    ]
