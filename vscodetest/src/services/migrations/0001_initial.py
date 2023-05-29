# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import common.classes


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
        ('orders', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('servicecatalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lifecycle', models.CharField(default='PROV', max_length=10, choices=[('ACTIVE', 'Active'), ('HISTORICAL', 'Historical'), ('PROV', 'Provisioning'), ('PROVFAILED', 'Provision Failed')])),
                ('attributes', models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True)),
                ('blueprint', models.ForeignKey(to='servicecatalog.ServiceBlueprint', on_delete=models.CASCADE)),
                ('group', models.ForeignKey(to='accounts.Group', on_delete=models.CASCADE)),
                ('jobs', models.ManyToManyField(to='jobs.Job', null=True, blank=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.UserProfile', null=True)),
            ],
            options={
            },
            bases=(models.Model, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='ServiceAppliance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('identifier', models.CharField(help_text='Identifier to tell external API what unique id to look for', max_length=255)),
                ('environment', models.ForeignKey(to='infrastructure.Environment', on_delete=models.CASCADE)),
                ('resource_handler', models.ForeignKey(to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('service', models.ForeignKey(to='services.Service', null=True, on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('identifier', models.CharField(help_text='Identifier to tell external API what unique id to look for', max_length=255)),
                ('appliance_identifier', models.CharField(help_text='Indentifier to tell external API what unique appliance id to look for. Appliances can be used to configure routing, firewall, load balances and other services', max_length=255, null=True)),
                ('environment', models.ForeignKey(to='infrastructure.Environment', on_delete=models.CASCADE)),
                ('network', models.ForeignKey(to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('resource_handler', models.ForeignKey(to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('service', models.ForeignKey(to='services.Service', null=True, on_delete=models.SET_NULL)),
                ('service_item', models.ForeignKey(to='servicecatalog.ServiceItem', null=True, on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
