# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0004_auto_20161004_2141'),
        ('puppet_ent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='peconf',
            name='console_api_connection',
            field=models.ForeignKey(related_name='console_api_connections', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='Console API Connection EndPoint', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peconf',
            name='db_api_connection',
            field=models.ForeignKey(related_name='db_api_connections', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='DB API Connection EndPoint', null=True),
            preserve_default=True,
        ),
    ]
