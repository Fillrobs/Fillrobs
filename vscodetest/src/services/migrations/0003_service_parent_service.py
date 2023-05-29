# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20161004_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='parent_service',
            field=models.ForeignKey(related_name='sub_components', on_delete=django.db.models.deletion.PROTECT, blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
    ]
