# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-21 23:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0010_currencyconversionrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyconversionrate',
            name='symbol',
            field=models.CharField(help_text='Ex. JPY, EUR, GBP, SEK, CHF, BRL, USD, etc', max_length=10),
        ),
    ]