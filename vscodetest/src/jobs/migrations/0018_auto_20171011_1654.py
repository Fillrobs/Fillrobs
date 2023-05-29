# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-11 16:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0017_deploy_blueprint_job_type_20171004_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')], max_length=50, verbose_name='Job type'),
        ),
        migrations.AlterField(
            model_name='recurringjob',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')], max_length=50, verbose_name='Job type'),
        ),
    ]
