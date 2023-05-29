# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0002_awshandler_awsvpcsubnet_ebsdisk_ec2serverinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='awshandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='aws.AmazonMachineImage', blank=True),
        ),
    ]
