# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cbhooks.models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailhook',
            name='body',
            field=models.TextField(help_text=cbhooks.models.emailhook_body_help_text, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='emailhook',
            name='from_address',
            field=models.CharField(help_text=cbhooks.models.emailhook_from_address_help_text, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remotescripthook',
            name='commandline_args',
            field=models.CharField(help_text=cbhooks.models.remotescripthook_commandline_args_help_text, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
