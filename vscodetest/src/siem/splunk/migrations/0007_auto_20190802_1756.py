# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-02 17:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splunk', '0006_auto_20190725_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='splunkprovider',
            name='installer_path',
            field=models.CharField(help_text="Path to SplunkForwarder tarball (.tgz) file on this server. Ensure that tarball is in /var/ or one of it's non-/tmp/ subdirectories, and is owned by the apache user.", max_length=255, verbose_name='Installer Path'),
        ),
    ]