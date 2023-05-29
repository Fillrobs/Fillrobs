# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azurearmhandler',
            name='networks',
            field=models.ManyToManyField(to='azure_arm.AzureARMSubnet', blank=True),
        ),
        migrations.AlterField(
            model_name='azurearmhandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='azure_arm.AzureARMImage', blank=True),
        ),
    ]
