# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibcloudImage',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=255)),
                ('external_id', models.CharField(max_length=100, null=True, blank=True)),
                ('uuid', models.CharField(max_length=100, null=True, blank=True)),
                ('extra', models.TextField(help_text='Tech-specific JSON data', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Image',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='LibcloudServerInfo',
            fields=[
                ('server', models.OneToOneField(primary_key=True, serialize=False, to='infrastructure.Server', on_delete=models.CASCADE)),
                ('location', models.CharField(max_length=100)),
                ('tags', models.TextField(default='', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
