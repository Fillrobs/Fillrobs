# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-06 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0044_environment_container_orchestrator'),
        ('servicecatalog', '0048_merge_20190730_2033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='installpodserviceitem',
            name='environment',
        ),
        migrations.AddField(
            model_name='installpodserviceitem',
            name='environments',
            field=models.ManyToManyField(to='infrastructure.Environment'),
        ),
    ]
