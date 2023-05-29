# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import costs.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(decimal_places=10, validators=[costs.models.isOnlyDigits], max_digits=65, blank=True, help_text='Enter the rate.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomFieldRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(decimal_places=10, validators=[costs.models.isOnlyDigits], max_digits=65, blank=True, help_text='Enter the rate.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LicenseRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(decimal_places=10, validators=[costs.models.isOnlyDigits], max_digits=65, blank=True, help_text='Enter the rate.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OSBuildRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(decimal_places=10, validators=[costs.models.isOnlyDigits], max_digits=65, blank=True, help_text='Enter the rate.', null=True)),
            ],
            options={
                'verbose_name': 'OS build rate',
            },
            bases=(models.Model,),
        ),
    ]
