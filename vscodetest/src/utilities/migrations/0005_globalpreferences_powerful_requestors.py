# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0004_auto_20161004_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='powerful_requestors',
            field=models.BooleanField(default=False, help_text='Allow requestors to change & delete all servers in their groups (not just the servers they are the owner of).', verbose_name='Powerful Requestors'),
            preserve_default=True,
        ),
    ]
