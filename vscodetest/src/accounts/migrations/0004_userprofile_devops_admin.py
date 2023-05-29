# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='devops_admin',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
