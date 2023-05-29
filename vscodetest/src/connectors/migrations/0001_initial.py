# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='the name of this Connector, eg.: Puppet', unique=True, max_length=80)),
                ('slug', models.CharField(help_text="For internal use; the connector's slug, as given by its manifest", unique=True, max_length=255)),
                ('app_name', models.CharField(help_text="For internal use; the connector's application name, as written for settings.INSTALLED_APPS..", unique=True, max_length=255)),
                ('inline_icon', models.ImageField(help_text='A 16px square icon that represents this connector.', upload_to='connector-icons', blank=True)),
                ('display_icon', models.ImageField(help_text='A 128px square icon that represents this connector.', upload_to='connector-icons', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConnectorConf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Label for this connector configuration', max_length=80)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='the name of this feature, eg.: install_application', unique=True, max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeatureMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('connector_conf', models.ForeignKey(to='connectors.ConnectorConf', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
