# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.classes
import common.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(help_text='Optional. Explain purpose or details about this group.', null=True, blank=True)),
                ('levels_to_show', models.IntegerField(default=None, help_text="How many levels of ancestors' names to show when this name is shown outside the context of the group hierarchy.", null=True, blank=True)),
                ('allow_auto_approval', models.BooleanField(default=False, help_text="Approve all orders for this group automatically. If not set, only approvers' and super admins' orders will be auto approved.", verbose_name="Auto approve requesters' orders")),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, common.mixins.HasCustomFieldValuesMixin, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_type', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Group Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('super_admin', models.BooleanField(default=False)),
                ('server_list_args', models.CharField(help_text='User-specific list filters and sort arguments', max_length=2000, null=True)),
                ('groups_default_view', models.CharField(default='resource usage', max_length=50, null=True, choices=[('resource usage', 'Resource Usage'), ('quota usage', 'Quota Usage')])),
                ('session_key', models.CharField(max_length=2000, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'User Profile',
            },
            bases=(models.Model,),
        ),
    ]
