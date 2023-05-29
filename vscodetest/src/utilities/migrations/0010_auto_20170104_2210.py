# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0009_remove_globalpreferences_enable_google_authentication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='show_rates_when_ordering',
            field=models.BooleanField(default=True, help_text='Display rate information when ordering servers.', verbose_name='Show rates when ordering'),
            preserve_default=True,
        ),
    ]
