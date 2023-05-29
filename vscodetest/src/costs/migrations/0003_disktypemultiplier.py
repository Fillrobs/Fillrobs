# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import costs.models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0008_diskstorage'),
        ('costs', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiskTypeMultiplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('multiplier', models.DecimalField(help_text='Enter the amount to multiply by.', max_digits=65, decimal_places=10, validators=[costs.models.isOnlyDigits])),
                ('disk_type', models.ForeignKey(to='infrastructure.DiskType', on_delete=models.CASCADE)),
                ('environment', models.ForeignKey(blank=True, to='infrastructure.Environment', help_text='If not set, this multiplier will apply to all environments.', null=True, on_delete=models.CASCADE)),
                ('rate_to_multiply', models.ForeignKey(blank=True, to='infrastructure.CustomField', help_text='Choose the rate to apply the multiplier to, or leave blank to apply to the total rate.', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='disktypemultiplier',
            unique_together=set([('environment', 'disk_type', 'rate_to_multiply')]),
        ),
    ]
