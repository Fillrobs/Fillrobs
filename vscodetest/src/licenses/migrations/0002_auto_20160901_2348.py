# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import licenses.models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='license_file',
            field=models.FileField(null=1, upload_to=licenses.models.license_license_file_upload_to, blank=1),
            preserve_default=True,
        ),
    ]
