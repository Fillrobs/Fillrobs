# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20161004_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='recently_viewed_items',
            field=models.CharField(help_text='JSON-formatted dict of collection name -> list of item IDs', max_length=2000, null=True),
            preserve_default=True,
        ),
    ]
