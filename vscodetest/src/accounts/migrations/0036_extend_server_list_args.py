# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-20 23:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_userprofile_global_viewer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='server_list_args',
            field=models.TextField(help_text='User-specific list filters and sort arguments', null=True),
        ),
    ]