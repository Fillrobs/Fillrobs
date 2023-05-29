# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-18 23:05
from __future__ import unicode_literals

import cb_secrets.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0064_auto_20190605_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectioninfo',
            name='headers',
            field=cb_secrets.fields.EncryptedTextField(blank=True, help_text='Encrypted json headers used for establishing remote connections. Used as a replacement for username:password configurations.', max_length=256, null=True, verbose_name='Headers'),
        ),
        migrations.AddField(
            model_name='connectioninfo',
            name='use_auth_headers',
            field=models.BooleanField(default=False),
        ),
    ]