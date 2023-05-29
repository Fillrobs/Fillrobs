# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_auto_20160901_2125'),
        ('cscv', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cittest',
            name='last_failed_date',
        ),
        migrations.RemoveField(
            model_name='cittest',
            name='last_success_date',
        ),
        migrations.AddField(
            model_name='cittest',
            name='last_job_failed',
            field=models.ForeignKey(related_name='failed_cit_test', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cittest',
            name='last_job_passed',
            field=models.ForeignKey(related_name='passed_cit_test', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cittest',
            name='last_status',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
    ]
