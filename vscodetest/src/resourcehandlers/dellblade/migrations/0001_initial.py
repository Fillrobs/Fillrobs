# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DellBladeHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
