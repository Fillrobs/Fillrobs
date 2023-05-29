# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-04 19:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0011_resourcehandler_enable_terminal_feature'),
        ('tags', '0006_cloudbolttag_sequence'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoCorrectTagValueMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correct_value', models.CharField(max_length=255)),
                ('miss_spelled_value', models.CharField(max_length=255)),
                ('resource_handler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='resourcehandlers.ResourceHandler')),
            ],
        ),
    ]
