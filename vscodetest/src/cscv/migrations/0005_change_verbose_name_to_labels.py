# -*- coding: utf-8 -*-
"""
No-op migration to change verbose_name from "Tags" to "Labels".
"""
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('cscv', '0004_populate_cit_test_stats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cittest',
            name='labels',
            field=taggit.managers.TaggableManager(to='tags.CloudBoltTag', through='tags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Labels'),
            preserve_default=True,
        ),
    ]
