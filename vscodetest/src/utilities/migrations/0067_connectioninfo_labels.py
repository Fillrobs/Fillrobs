# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-29 15:22
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0010_set_bidirectional_sync_on_taggableattribute_20190419_2105'),
        ('utilities', '0066_servicenow'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectioninfo',
            name='labels',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='tags.TaggedItem', to='tags.CloudBoltTag', verbose_name='Tags'),
        ),
    ]
