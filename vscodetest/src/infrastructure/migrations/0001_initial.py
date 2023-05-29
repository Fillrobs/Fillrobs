# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.classes
import infrastructure.models
import common.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Alphanumeric characters, starting with a letter, with optional underscores.', unique=True, max_length=255)),
                ('label', models.CharField(max_length=50)),
                ('description', models.TextField(help_text='May be used to explain the purpose of a custom field and offer guidance to users.  If set, will be shown on order form and elsewhere in order to improve the user experience.', null=True, blank=True)),
                ('type', models.CharField(max_length=6, choices=[('STR', 'String'), ('INT', 'Integer'), ('IP', 'IP Address'), ('DT', 'Date & Time'), ('TXT', 'Multi-line Text'), ('ETXT', 'Encrypted Text'), ('CODE', 'Code'), ('BOOL', 'Boolean'), ('DEC', 'Decimal'), ('NET', 'Network'), ('PWD', 'Password'), ('TUP', 'Tuple'), ('LDAP', 'LDAPUtility'), ('URL', 'URL'), ('NSXS', 'NSX Scope'), ('NSXE', 'NSX Edge')])),
                ('hide_single_value', models.BooleanField(default=False)),
                ('required', models.BooleanField(default=False)),
                ('show_on_servers', models.BooleanField(default=False)),
                ('available_all_servers', models.BooleanField(default=False)),
                ('value_pattern_string', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=255, db_index=True)),
                ('computed_address', models.CharField(max_length=255, null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('geocode_error', models.CharField(default='', max_length=1024, blank=True)),
                ('name', models.CharField(max_length=55)),
            ],
            options={
                'ordering': ('longitude',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Disk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=255)),
                ('disk_size', models.IntegerField(verbose_name='Disk size (GB)')),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=55)),
                ('description', models.TextField(help_text='Optional. Explain purpose or details about this environment.', null=True, blank=True)),
                ('auto_approval', models.BooleanField(default=False, help_text="Approve all orders for this environment automatically. If not set, only approvers' and super admins' orders will be auto approved.", verbose_name="Auto approve requesters' orders")),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Environment',
            },
            bases=(common.mixins.HasCustomFieldValuesMixin, models.Model, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Preconfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('label', models.CharField(max_length=100)),
                ('include_os_build', models.BooleanField(default=False)),
                ('include_applications', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, null=1, blank=1)),
                ('global_scope', models.BooleanField(default=False)),
                ('include_hostname', models.BooleanField(default=False, verbose_name='Provides hostnames')),
                ('include_ipaddress', models.BooleanField(default=False, verbose_name='Provides IP addresses')),
                ('include_mac', models.BooleanField(default=False, verbose_name='Provides MAC addresses')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePoolValueSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=200, blank=True)),
                ('ip', models.CharField(max_length=200, verbose_name='IP', blank=True)),
                ('mac', models.CharField(max_length=200, blank=True)),
                ('cpu_cnt', models.IntegerField(null=True, verbose_name='Number of CPUs', blank=True)),
                ('disk_size', models.IntegerField(null=True, verbose_name='Disk size (GB)', blank=True)),
                ('mem_size', models.DecimalField(null=True, verbose_name='Memory size (GB)', max_digits=10, decimal_places=4, blank=True)),
                ('hw_rate', models.DecimalField(null=True, verbose_name='Hardware Rate', max_digits=65, decimal_places=10, blank=True)),
                ('sw_rate', models.DecimalField(null=True, verbose_name='Software Rate', max_digits=65, decimal_places=10, blank=True)),
                ('extra_rate', models.DecimalField(null=True, verbose_name='Extra Rate', max_digits=65, decimal_places=10, blank=True)),
                ('total_rate', models.DecimalField(null=True, verbose_name='Total Rate', max_digits=65, decimal_places=10, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=200, blank=True)),
                ('ip', models.CharField(max_length=200, verbose_name='IP', blank=True)),
                ('mac', models.CharField(max_length=200, blank=True)),
                ('cpu_cnt', models.IntegerField(null=True, verbose_name='Number of CPUs', blank=True)),
                ('disk_size', models.IntegerField(null=True, verbose_name='Disk size (GB)', blank=True)),
                ('mem_size', models.DecimalField(null=True, verbose_name='Memory size (GB)', max_digits=10, decimal_places=4, blank=True)),
                ('hw_rate', models.DecimalField(null=True, verbose_name='Hardware Rate', max_digits=65, decimal_places=10, blank=True)),
                ('sw_rate', models.DecimalField(null=True, verbose_name='Software Rate', max_digits=65, decimal_places=10, blank=True)),
                ('extra_rate', models.DecimalField(null=True, verbose_name='Extra Rate', max_digits=65, decimal_places=10, blank=True)),
                ('total_rate', models.DecimalField(null=True, verbose_name='Total Rate', max_digits=65, decimal_places=10, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('add_date', models.DateTimeField(auto_now_add=True, help_text='Date the server with this UUID was discovered by or created by CB.  If a server becomes historical and then active again, the date will remain the original date.', null=True, verbose_name='date added')),
                ('status', models.CharField(default='ACTIVE', help_text='\n            Changing the status is useful if a server gets stuck in\n            the wrong state. Setting status to historical is like deleting a\n            server except that history is retained.\n        ', max_length=10, choices=[('ACTIVE', 'Active'), ('DECOM', 'Deleting'), ('HISTORICAL', 'Historical'), ('MODIFY', 'Modifying'), ('PROVFAILED', 'Provision Failed'), ('PROV', 'Provisioning')])),
                ('provision_engine_svr_id', models.CharField(max_length=200, blank=1)),
                ('resource_handler_svr_id', models.CharField(max_length=200, blank=1)),
                ('power_status', models.CharField(default='UNKNOWN', max_length=10, editable=False, choices=[('POWEROFF', 'off'), ('POWERON', 'on'), ('SUSPENDED', 'suspended'), ('UNKNOWN', 'Unknown')])),
            ],
            options={
                'abstract': False,
            },
            bases=(infrastructure.models.ClonableMixin, models.Model, common.mixins.HasCustomFieldValuesMixin, common.classes.AutoCompleteMixin),
        ),
    ]
