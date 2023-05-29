# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cb_secrets.fields
import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceHandler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Display name. Not used in any programmatic fashion and can be changed safely.', max_length=50)),
                ('description', models.TextField(help_text='Optional. Explain purpose or details about this resource handler.', null=True, blank=True)),
                ('ip', models.CharField(max_length=50, verbose_name='IP address', validators=[common.validators.validate_domain_or_ip])),
                ('port', models.IntegerField(default=443, help_text='Port used to connect to this resource handler', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(help_text='Protocol used to connect to this resource handler', max_length=10, choices=[('http', 'http'), ('https', 'https'), ('ssh', 'ssh'), ('udp', 'udp')])),
                ('serviceaccount', models.CharField(help_text='Username of account authorized to run commands on this resource handler', max_length=250, verbose_name='Account username')),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(verbose_name='Account password')),
                ('ignore_vm_names', models.TextField(help_text="A comma separated list of the names of VMs to exclude during VM synchronization. These names are regular expressions, and any whitespace surrounding each rule will be ignored. Ex. 'proddb.*, joetest1, .*qalab.*'. If a rule is introduced which ignores a VM already managed by CloudBolt, that VM will be marked historical in CloudBolt after the next sync.", null=True, blank=True)),
                ('ignore_vm_folders', models.TextField(help_text="A comma separated list of the folders of VMs to exclude during VM synchronization. These folders names are regular expressions. Ex. 'Secure Servers.*, AD Servers'. Specifying this field will slow down VM synchronization jobs for some technologies (ex. VMware). If a rule is introduced which ignores a VM already managed by CloudBolt, that VM will be marked historical in CloudBolt after the next sync.", null=True, blank=True)),
                ('custom_fields', models.ManyToManyField(to='infrastructure.CustomField', null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceLimitItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maximum', models.IntegerField(default=None, help_text='Value of -1 indicates infinite resources.')),
                ('custom_field', models.ForeignKey(to='infrastructure.CustomField', on_delete=models.CASCADE)),
                ('handler', models.ForeignKey(verbose_name='Resource Handler', to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Display name for the network. Not used in any programmatic fashion and can be changed safely.', max_length=100)),
                ('description', models.TextField(help_text='Optional. Explain purpose or details about this network.', null=True, blank=True)),
                ('network', models.CharField(help_text='Identifying name/ID of the network. Used as an identifier and should not be changed.', max_length=100)),
                ('vlan', models.IntegerField(blank=True, null=True, validators=[common.validators.is_only_digits])),
                ('netmask', models.CharField(max_length=15, null=True, blank=True)),
                ('gateway', models.CharField(max_length=15, null=True, blank=True)),
                ('dns1', models.CharField(max_length=15, null=True, verbose_name='DNS 1', blank=True)),
                ('dns2', models.CharField(max_length=15, null=True, verbose_name='DNS 2', blank=True)),
                ('dns_domain', models.CharField(max_length=50, null=True, verbose_name='DNS Domain', blank=True)),
                ('addressing_schema', models.CharField(default='dhcp', max_length=10, choices=[('dhcp', 'DHCP only'), ('static', 'Static only'), ('both', 'User defined')])),
                ('nat_info', models.CharField(max_length=50, null=True, verbose_name='NAT Info', blank=True)),
                ('custom_field_values', models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True)),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name of the resource technology (ex. VMware)')),
                ('version', models.CharField(max_length=20, verbose_name='Version of the resource technology')),
                ('modulename', models.CharField(max_length=50, verbose_name='Python module for interacting with this version of this resource management technology.', blank=1)),
            ],
            options={
                'verbose_name_plural': 'Resource technologies',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='resourcelimititem',
            unique_together=set([('handler', 'custom_field')]),
        ),
        migrations.AddField(
            model_name='resourcehandler',
            name='limit_fields',
            field=models.ManyToManyField(related_name='limit_fields', through='resourcehandlers.ResourceLimitItem', to='infrastructure.CustomField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcehandler',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcehandler',
            name='resource_technology',
            field=models.ForeignKey(to='resourcehandlers.ResourceTechnology', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
