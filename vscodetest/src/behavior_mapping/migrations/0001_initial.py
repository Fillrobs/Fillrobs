# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFieldMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('required', models.BooleanField(default=False)),
                ('hide_single_value', models.BooleanField(default=False)),
                ('maximum', models.DecimalField(help_text='For string types, the max length. For integers & decimals, the maximum value.  For dates, the maximum number of days from today.', null=True, max_digits=10, decimal_places=2, blank=True)),
                ('minimum', models.DecimalField(help_text='For string types, the min length. For integers & decimals, the maximum value.', null=True, max_digits=10, decimal_places=2, blank=True)),
                ('regex_constraint', models.CharField(default='', max_length=250)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreconfigurationMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePoolMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
