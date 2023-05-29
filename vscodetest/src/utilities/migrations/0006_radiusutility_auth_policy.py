# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0005_globalpreferences_powerful_requestors'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiusutility',
            name='auth_policy',
            field=models.CharField(default='TOKEN', max_length=15, choices=[('TOKEN', 'Token Only'), ('PIN+TOKEN', 'Password + Token'), ('TOKEN+PIN', 'Token + Password')]),
            preserve_default=True,
        ),
    ]
