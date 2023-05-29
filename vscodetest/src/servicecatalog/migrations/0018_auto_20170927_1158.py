# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 11:58
from __future__ import unicode_literals

import common.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0017_auto_20170727_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installpodserviceitem',
            name='container_orchestrator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='containerorchestrators.ContainerOrchestrator', verbose_name='Container Orchestrator'),
        ),
        migrations.AlterField(
            model_name='installpodserviceitem',
            name='images',
            field=models.TextField(blank=True, default='', help_text='Comma-separated list of images of containers to install as part of this pod', verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='provisionserverserviceitem',
            name='hostname_template',
            field=models.CharField(default='', max_length=255, verbose_name='Hostname Template'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='any_group_can_deploy',
            field=models.BooleanField(default=False, help_text='Allow any group to order the Blueprint, rather than only giving deploy permissions to specific groups.', verbose_name='Any group can deploy'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='create_service',
            field=models.BooleanField(default=True, help_text='Specify whether ordering the Blueprint should create a service or simply provision any included servers.', verbose_name='Create service'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='list_image',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Any size. All standard image formats work, though PNGs with alpha transparency look best.', null=True, upload_to='services/', verbose_name='List Image'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='name',
            field=models.CharField(max_length=75, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence specifies the order (followed by blueprint name) that blueprints appear in the catalog. Lower-number sequence numbers will show up first. (default=0)', verbose_name='Sequence'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='service_name_template',
            field=models.CharField(blank=True, help_text='Specify a template for generating deployed service names', max_length=255, null=True, verbose_name='Service Name Template'),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('HISTORICAL', 'Historical')], default='ACTIVE', max_length=10, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='deploy_seq',
            field=models.IntegerField(blank=True, help_text='Order in which blueprint items of a service will be deployed.', null=True, verbose_name='Deploy Sequence'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='description',
            field=models.TextField(blank=True, help_text='Optional detailed description about this blueprint item for end users.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='execute_in_parallel',
            field=models.BooleanField(default=False, verbose_name='Execute in Parallel'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='name',
            field=models.CharField(blank=True, help_text='Optional name to identify this blueprint item to end users.', max_length=75, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='show_on_order_form',
            field=models.BooleanField(default=True, verbose_name='Show on Order Form'),
        ),
    ]
