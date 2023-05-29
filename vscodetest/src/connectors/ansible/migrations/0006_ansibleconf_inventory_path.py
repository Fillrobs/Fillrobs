# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0005_auto_20161209_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='ansibleconf',
            name='inventory_path',
            field=models.CharField(default='/home/ansible/cloudbolt.py', help_text='The full path to this playbook on the management server.', max_length=255),
            preserve_default=True,
        ),
    ]
