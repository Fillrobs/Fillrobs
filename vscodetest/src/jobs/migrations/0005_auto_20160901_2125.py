# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hookparameters',
            name='hookjobparameters_ptr',
            field=models.OneToOneField(parent_link=True, related_name='hookparameters', primary_key=True, db_column='jobparameters_ptr_id', serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
