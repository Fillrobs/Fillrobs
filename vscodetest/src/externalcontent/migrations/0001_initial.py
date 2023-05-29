# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.classes
import common.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OSBuild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(help_text='Optional. Explain purpose or details about this OS build.', null=True, blank=True)),
                ('use_handler_template', models.BooleanField(default=False, verbose_name='Use Template Provisioning')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'OS Build',
                'verbose_name_plural': 'OS Builds',
            },
            bases=(models.Model, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='OSBuildAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(common.mixins.HasCustomFieldValuesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OSFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('inline_icon', models.ImageField(help_text='a 16x16px icon', upload_to='osfamily-icons', blank=True)),
                ('display_icon', models.ImageField(help_text='a 128x128px icon', upload_to='osfamily-icons', blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='externalcontent.OSFamily', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'OS Family',
                'verbose_name_plural': 'OS Families',
            },
            bases=(models.Model, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='OSVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VendorApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application', models.ForeignKey(to='externalcontent.Application', on_delete=models.CASCADE)),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
