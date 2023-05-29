# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-13 13:43
from __future__ import unicode_literals

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0051_merge_20190815_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=12, verbose_name='Global ID'),
        ),
    ]
