# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-02 19:02
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0020_serviceblueprint_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceblueprint',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='tags.TaggedItem', to='tags.CloudBoltTag', verbose_name='Labels'),
        ),
    ]
