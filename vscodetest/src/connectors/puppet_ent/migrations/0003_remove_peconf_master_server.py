# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puppet_ent', '0002_auto_20161006_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peconf',
            name='master_server',
        ),
    ]
