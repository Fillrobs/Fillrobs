# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import common.classes


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cbhooks', '0001_initial'),
        ('infrastructure', '0001_initial'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jobid', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100, null=1, blank=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50, verbose_name='Job type', choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('install_service', 'Install Service'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')])),
                ('status', models.CharField(default='PENDING', max_length=10, verbose_name='Job status', choices=[('PENDING', 'Pending'), ('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('SUCCESS', 'Completed successfully'), ('WARNING', 'Completed with warnings'), ('FAILURE', 'Completed with errors'), ('TO_CANCEL', 'In cancellation process'), ('CANCELED', 'Canceled by user')])),
                ('start_date', models.DateTimeField(verbose_name='Time started', null=1, editable=False, blank=1)),
                ('end_date', models.DateTimeField(verbose_name='Time completed', null=1, editable=False, blank=1)),
                ('output', models.TextField(verbose_name='Job output', blank=1)),
                ('errors', models.TextField(verbose_name='Job errors', blank=1)),
                ('tasks_done', models.PositiveIntegerField(null=1, blank=1)),
                ('total_tasks', models.PositiveIntegerField(null=1, blank=1)),
            ],
            options={
                'get_latest_by': 'start_date',
            },
            bases=(models.Model, common.classes.AutoCompleteMixin),
        ),
        migrations.CreateModel(
            name='JobParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('failure_email_address', models.CharField(max_length=255, null=True, verbose_name='If the job fails, send an e-amil to this address', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallApplicationsParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='HookParameters',
            fields=[
                ('hookjobparameters_ptr', models.OneToOneField(parent_link=True, related_name='jobs_hookparameters_related', primary_key=True, db_column='jobparameters_ptr_id', serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('_arguments', models.TextField(help_text='JSON representation of the dictionary of name/value pairs to be passed to this action.')),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='FunctionalTestParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('run_full_suite', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='DeleteSnapshotsParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='CFVChangeParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='ManageNICsParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='NetworkActionParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nic_index', models.PositiveIntegerField()),
                ('network_action', models.CharField(default='CREATE', max_length=10, verbose_name='Network Action', choices=[('CREATE', 'Add a new NIC'), ('UPDATE', 'Update an existing NIC'), ('DELETE', 'Delete an existing NIC')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgressMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=10000, null=1, verbose_name='Progress message', blank=1)),
                ('detailed_message', models.TextField(default='', help_text='A detailed message that will not be shown by default, but which a user can select to see details.')),
                ('file_location', models.CharField(default='', help_text='Used for progress messages that have an accompanying file where output is being streamed.', max_length=1024)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Time of entry')),
            ],
            options={
                'get_latest_by': 'id',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RunFlowParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('run_mode', models.CharField(default='execute', max_length=15, choices=[('execute_async', 'Asynchronous Execution'), ('execute', 'Synchronous Execution')])),
                ('_flow_inputs', models.TextField(default='{}', help_text='The input values to be used in the flow execution as JSON', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='SyncSvrsFromPEsParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='SyncUsersFromLdapParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='SyncVMParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='TriggerActionParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('_arguments', models.TextField(help_text='JSON representation of the dictionary of name/value pairs to be passed to this action.')),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='cbhooks.HookPointAction', null=True)),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='cbhooks.TriggerPoint', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='TriggerParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('trigger_point_id', models.PositiveIntegerField(null=True)),
                ('_arguments', models.TextField(help_text='JSON representation of the dictionary of name/value pairs to be passed to this action.')),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
        migrations.CreateModel(
            name='UninstallApplicationsParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jobs.JobParameters', on_delete=models.CASCADE)),
                ('applications', models.ManyToManyField(to='externalcontent.Application')),
                ('servers', models.ManyToManyField(to='infrastructure.Server')),
            ],
            options={
                'abstract': False,
            },
            bases=('jobs.jobparameters',),
        ),
    ]
