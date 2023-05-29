# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-27 19:55
from __future__ import unicode_literals

import common.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20171127_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcetype',
            name='name',
            field=models.CharField(help_text='Alphanumeric characters, starting with a letter, with optional underscores.', max_length=50, unique=True, validators=[common.validators.valid_python_identifier]),
        ),
    ]
