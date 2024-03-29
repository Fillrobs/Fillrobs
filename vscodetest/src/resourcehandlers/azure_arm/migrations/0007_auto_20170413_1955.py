# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-13 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0006_azurearmserverinfo_storage_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azurearmhandler',
            name='client_id',
            field=models.CharField(help_text="The ID of an Active Directory application to use. Azure's documentation also refers to this as 'Client ID'.", max_length=256, verbose_name='Application ID'),
        ),
        migrations.AlterField(
            model_name='azurearmhandler',
            name='secret',
            field=models.CharField(help_text="A private key created for the given Active Directory application. Azure's documentation describes how to generate this type of key, but will only display the value once when it is generated.", max_length=256, verbose_name='Authentication Key'),
        ),
        migrations.AlterField(
            model_name='azurearmhandler',
            name='tenant_id',
            field=models.CharField(help_text="The Directory ID for the given Active Directory application. In Azure's portal, this property is listed as 'Directory ID', but Azure's documentation also refers to it as 'Tenant ID'.", max_length=256, verbose_name='Directory ID'),
        ),
    ]
