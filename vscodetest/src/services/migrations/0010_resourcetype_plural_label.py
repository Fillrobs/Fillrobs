# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-16 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_merge_20171116_1846'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcetype',
            name='plural_label',
            field=models.CharField(blank=True, help_text='Optional label for plural references to this Resource Type. If not set, defaults to adding an "s" to the label.', max_length=255, null=True),
        ),
    ]
