# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-30 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0035_auto_20180514_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='serveraction',
            name='sequence',
            field=models.PositiveIntegerField(blank=True, help_text='A positive integer that describes how this Server Action should be sequenced relative to other Server Actions when displayed, such as for the buttons on a Server. Server Actions with a sequence of 0 will appear first, then in order of increasing sequence, followed by any Server Actions without a sequence. Groups of Server Actions with the same sequence will be sorted secondarily by label.', null=True, verbose_name='Display sequence'),
        ),
    ]
