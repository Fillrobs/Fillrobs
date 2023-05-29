# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reportengines', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JasperReportingEngine',
            fields=[
                ('reportingengine_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='reportengines.ReportingEngine', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('reportengines.reportingengine',),
        ),
    ]
