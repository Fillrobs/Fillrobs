# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-17 01:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0044_auto_20190906_0016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azurearmhandler',
            name='auth_type',
            field=models.CharField(choices=[('SERVICE', 'Service Principal'), ('ADAL', 'Active Directory')], default='SERVICE', max_length=128, verbose_name='Auth Type'),
        ),
        migrations.AlterField(
            model_name='azurearmhandler',
            name='cloud_environment',
            field=models.CharField(choices=[('PUBLIC', 'Public (Default)'), ('GERMAN', 'Germany'), ('CHINA', 'China'), ('US_GOV', 'US Gov')], default='PUBLIC', max_length=128, verbose_name='Cloud Environment'),
        ),
    ]
