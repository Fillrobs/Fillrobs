# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cb_secrets.fields
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_value', models.CharField(max_length=975, null=1, blank=1)),
                ('pwd_value', cb_secrets.fields.EncryptedPasswordField(null=1, blank=1)),
                ('txt_value', models.TextField(max_length=6000, null=1, blank=1)),
                ('datetime_value', models.DateTimeField(null=1, blank=1)),
                ('file_value', models.FileField(null=1, upload_to='/home/david/var/opt/cloudbolt/filefields/', blank=1)),
                ('email_value', models.EmailField(max_length=75, null=1, blank=1)),
                ('boolean_value', models.NullBooleanField()),
                ('decimal_value', models.DecimalField(null=1, max_digits=15, decimal_places=10, blank=1)),
                ('int_value', models.IntegerField(null=1, blank=1)),
                ('ip_value', models.CharField(max_length=255, null=1, blank=1)),
                ('url_value', models.URLField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallServiceItemOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(null=True)),
                ('hostname', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default='', max_length=1024, blank=1)),
                ('name_pristine', models.BooleanField(default=True, help_text='\n            Set to False when the name field has been overridden by a\n            user. If True, CB will continue to overwrite the name whenever\n            items are added or removed from the order. If False, this indicates\n            that the user has added a more meaningful name and CB will no\n            longer change the name.\n            ')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('denied_reason', models.TextField(max_length=1024, null=True, verbose_name='Reason Denied', blank=1)),
                ('approve_date', models.DateTimeField(verbose_name='date approved', null=1, editable=False, blank=1)),
                ('comment', models.CharField(max_length=200, null=True, verbose_name='Order Comment', blank=1)),
                ('status', models.CharField(default='CART', max_length=10, editable=False, blank=0, choices=[('CART', 'Not yet submitted'), ('INTERNAL', 'Internal use only'), ('PENDING', 'Pending approval'), ('ACTIVE', 'Active'), ('COMPLETE', 'Complete'), ('SUCCESS', 'Completed successfully'), ('WARNING', 'Completed with warnings'), ('FAILURE', 'Completed with errors'), ('HISTORICAL', 'Historical'), ('DENIED', 'Denied'), ('CANCELED', 'Canceled')])),
                ('last_reminder_sent_date', models.DateTimeField(null=True, verbose_name='date last reminder sent', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('add_date', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters', models.Model),
        ),
        migrations.CreateModel(
            name='InstallServiceOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
                ('service_name', models.CharField(default='', max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem',),
        ),
        migrations.CreateModel(
            name='InstallPodOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
                ('images', models.TextField()),
                ('name', models.CharField(max_length=75)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem',),
        ),
        migrations.CreateModel(
            name='DecomServerOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
                ('pre_decom', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem',),
        ),
        migrations.CreateModel(
            name='PreconfigurationValueSet',
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
                ('value', models.CharField(max_length=200, blank=True)),
                ('display_order', models.FloatField(default=1.0, help_text='Determines the ordering of the options on the new server form (lower values come first)')),
            ],
            options={
                'ordering': ['display_order', 'value'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProvisionNetworkOrderItem',
            fields=[
                ('hookparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='jobs.HookParameters', on_delete=models.CASCADE)),
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem', 'jobs.hookparameters'),
        ),
        migrations.CreateModel(
            name='ProvisionServerOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
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
                ('quantity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('applications', models.ManyToManyField(to='externalcontent.Application', null=True, blank=True)),
                ('custom_field_values', models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True)),
                ('os_build', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True)),
                ('preconfiguration_values', models.ManyToManyField(to='orders.PreconfigurationValueSet', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem', models.Model),
        ),
        migrations.CreateModel(
            name='ServerModOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.OrderItem', on_delete=models.CASCADE)),
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
                ('power_action', models.IntegerField(default=1)),
                ('applications', models.ManyToManyField(to='externalcontent.Application', null=True, blank=True)),
                ('custom_field_values', models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True)),
                ('disk', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Disk', help_text='The disk to be modified', null=True)),
                ('original_custom_field_values', models.ManyToManyField(related_name='mod_oi_orig_values_set', null=True, to='orders.CustomFieldValue', blank=True)),
                ('os_build', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True)),
                ('server', models.ForeignKey(to='infrastructure.Server', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('orders.orderitem', models.Model),
        ),
    ]
