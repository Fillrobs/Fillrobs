# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-15 23:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0007_autocorrecttagvaluemapping'),
    ]

    operations = [
        migrations.RenameField(
            model_name='autocorrecttagvaluemapping',
            old_name='miss_spelled_value',
            new_name='misspelled_value',
        ),
    ]