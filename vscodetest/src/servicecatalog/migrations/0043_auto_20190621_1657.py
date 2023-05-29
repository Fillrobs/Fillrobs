# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-21 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0042_copyfileactionserviceitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='copyfileactionserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='runcloudbolthookserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='runemailhookserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='runflowhookserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='runremotescripthookserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='runwebhookserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='serviceblueprint',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
        migrations.AddField(
            model_name='teardownserviceitem',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
    ]
