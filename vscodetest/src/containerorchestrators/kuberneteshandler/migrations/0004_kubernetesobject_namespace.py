# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-14 23:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kuberneteshandler', '0003_rename_to_kubernetesobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='kubernetesobject',
            name='namespace',
            field=models.CharField(default='default', max_length=253),
        ),
    ]
