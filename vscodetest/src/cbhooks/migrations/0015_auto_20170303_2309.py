# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-03 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0014_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hookpoint',
            name='job_type',
            field=models.CharField(blank=True, choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('install_service', 'Deploy Blueprint'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')], max_length=50, null=True, verbose_name='Job Type'),
        ),
    ]
