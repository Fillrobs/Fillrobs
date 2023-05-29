# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='enable_google_authentication',
            field=models.BooleanField(default=False, verbose_name='Google authentication'),
            preserve_default=True,
        ),
    ]
