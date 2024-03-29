# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-23 18:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0033_auto_20180607_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='favorited',
            field=models.BooleanField(
                default=False, help_text='Favorited blueprints appear at the top of the catalog when sorting by Featured, regardless of sequence.', verbose_name='Favorite'),
        ),
    ]
