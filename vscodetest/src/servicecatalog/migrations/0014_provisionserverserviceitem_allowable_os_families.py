# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 14:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0005_auto_20170325_1506'),
        ('servicecatalog', '0013_auto_20170405_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='provisionserverserviceitem',
            name='allowable_os_families',
            field=models.ManyToManyField(blank=True, help_text='When an OS Build is chosen, only show options for OS Builds with these families. This applies when ordering the blueprint (if the tier is set to allow the user to choose an OS Build), and when the OS Build is set on the tier.', to='externalcontent.OSFamily', verbose_name='Allowable OS Families'),
        ),
    ]
