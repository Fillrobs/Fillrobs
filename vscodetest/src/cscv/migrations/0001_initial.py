# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CITConf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CITTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('expected_status', models.CharField(max_length=25, choices=[('SUCCESS', 'complete with success'), ('WARNING', 'complete with warnings'), ('FAILURE', 'complete with errors')])),
                ('expected_output', models.TextField(help_text='Expected output will search for matching job results. Leaving blank will search for any result found.', blank=True)),
                ('last_failed_date', models.DateTimeField(null=True)),
                ('last_success_date', models.DateTimeField(null=True)),
                ('last_duration', models.CharField(help_text='Last duration is displayed in seconds', max_length=64, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
                ('notes', models.TextField(help_text='Notes to identify the purpose of the CITTest', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActionCITTest',
            fields=[
                ('cittest_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cscv.CITTest', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('cscv.cittest', models.Model),
        ),
        migrations.AddField(
            model_name='cittest',
            name='cit_conf',
            field=models.ForeignKey(to='cscv.CITConf', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
