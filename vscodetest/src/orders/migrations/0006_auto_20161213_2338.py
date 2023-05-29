# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20161004_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldvalue',
            name='email_value',
            field=models.EmailField(max_length=254, null=1, blank=1),
        ),
    ]
