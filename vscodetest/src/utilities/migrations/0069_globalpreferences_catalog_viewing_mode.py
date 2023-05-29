# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-12 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0068_auto_20190807_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='catalog_viewing_mode',
            field=models.CharField(choices=[('tiles', 'tiles'), ('table', 'table')], default='tiles', help_text='This controls how blueprints will be organized and styled when browsing the Catalog page.', max_length=255, verbose_name='Default Catalog Viewing Mode'),
        ),
    ]