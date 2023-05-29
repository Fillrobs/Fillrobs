# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceitem',
            name='show_on_order_form',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
