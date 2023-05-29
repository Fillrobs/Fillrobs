# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orders.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldvalue',
            name='file_value',
            field=models.FileField(null=1, upload_to=orders.models.customfieldvalue_file_value_upload_to, blank=1),
            preserve_default=True,
        ),
    ]
