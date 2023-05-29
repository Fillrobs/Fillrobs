# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrationengines', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VCO',
            fields=[
                ('orchestrationengine_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orchestrationengines.OrchestrationEngine', on_delete=models.CASCADE)),
                ('folder', models.CharField(max_length=200, verbose_name='Base folder for discoverable flows')),
            ],
            options={
                'abstract': False,
            },
            bases=('orchestrationengines.orchestrationengine',),
        ),
    ]
