# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0008_connectioninfo_ssh_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='globalpreferences',
            name='enable_google_authentication',
        ),
    ]
