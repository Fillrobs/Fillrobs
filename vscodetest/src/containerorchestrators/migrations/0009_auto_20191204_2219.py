# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-04 22:19
from __future__ import unicode_literals

import common.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containerorchestrators', '0008_auto_20190325_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containerorchestrator',
            name='port',
            field=models.IntegerField(blank=True, help_text='Port used to connect to this Container Orchestrator', null=True, validators=[common.validators.is_only_digits]),
        ),
        migrations.AlterField(
            model_name='containerorchestrator',
            name='protocol',
            field=models.CharField(choices=[('https', 'https'), ('http', 'http')], default='https', help_text='Protocol used to connect to this Container Orchestrator', max_length=10),
        ),
        migrations.AlterField(
            model_name='containerorchestrator',
            name='serviceaccount',
            field=models.CharField(help_text='Username of account authorized to run commands on this Container Orchestrator', max_length=250, verbose_name='Account username'),
        ),
    ]
