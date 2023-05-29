# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 23:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_installpod_add_config_file'),
        ('files', '0003_fileinput'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileInputMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_value', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.CustomFieldValue')),
                ('file_input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.FileInput')),
            ],
        ),
    ]
