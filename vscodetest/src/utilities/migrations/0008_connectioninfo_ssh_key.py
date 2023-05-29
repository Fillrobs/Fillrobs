# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20161004_2141'),
        ('utilities', '0007_auto_20161021_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectioninfo',
            name='ssh_key',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='orders.CustomFieldValue', help_text='If an SSH key is selected and a script is run on this connection with SSH, any password entered will be ignored in favor of using the chosen key.', null=True, verbose_name='SSH Key'),
            preserve_default=True,
        ),
    ]
