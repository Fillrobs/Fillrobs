# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerExpireParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='ServerNetworkCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('mac', models.CharField(max_length=20)),
                ('ip', models.CharField(max_length=20, null=True, blank=True)),
                ('private_ip', models.CharField(default='', max_length=20, null=True, blank=True)),
                ('bootproto', models.CharField(default='none', max_length=10, blank=True, choices=[('none', 'None'), ('dhcp', 'DHCP'), ('static', 'Static')])),
            ],
            options={
                'ordering': ['index'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(help_text='Date this snapshot was taken on the server', auto_now_add=True, null=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.TextField(max_length=512, null=True, blank=True)),
                ('identifier', models.CharField(max_length=50)),
                ('server', models.ForeignKey(to='infrastructure.Server', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
