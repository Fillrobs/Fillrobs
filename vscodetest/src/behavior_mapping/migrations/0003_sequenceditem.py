# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0005_auto_20160829_2059'),
        ('behavior_mapping', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='SequencedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seq', models.IntegerField(help_text='Order in which item will be displayed in forms and elsewhere', null=True, blank=True)),
                ('other_name', models.CharField(default='', max_length=250)),
                ('other_label', models.CharField(default='', max_length=250)),
                ('custom_field', models.ForeignKey(blank=True, to='infrastructure.CustomField', null=True, on_delete=models.CASCADE)),
                ('preconfig', models.ForeignKey(blank=True, to='infrastructure.Preconfiguration', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['seq', 'id'],
            },
            bases=(models.Model,),
        ),
    ]
