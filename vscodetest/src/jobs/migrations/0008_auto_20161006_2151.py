# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20161004_2141'),
        ('jobs', '0007_auto_20161004_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurringJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(default='', blank=True)),
                ('type', models.CharField(max_length=50, verbose_name='Job type', choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('install_service', 'Install Service'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')])),
                ('schedule', models.CharField(help_text='Cron-style string that specifies when this job should run.', max_length=255)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Time created', editable=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='accounts.UserProfile', null=True)),
                ('parameters', models.ForeignKey(to='jobs.JobParameters', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='job',
            name='recurring_job',
            field=models.ForeignKey(related_name='spawned_jobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.RecurringJob', null=True),
            preserve_default=True,
        ),
    ]
