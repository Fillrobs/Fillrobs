# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('provisionengines', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RazorRepository',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('name', models.CharField(max_length=50, verbose_name='Razor repository name')),
            ],
            options={
                'verbose_name': 'Razor repository',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='RazorServer',
            fields=[
                ('provisionengine_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='provisionengines.ProvisionEngine', on_delete=models.CASCADE)),
                ('repositories', models.ManyToManyField(to='razor.RazorRepository', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Razor Server',
            },
            bases=('provisionengines.provisionengine',),
        ),
    ]
