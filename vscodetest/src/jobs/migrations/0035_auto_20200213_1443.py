# Generated by Django 2.2.10 on 2020-02-13 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0034_auto_20190613_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots'), ('action', 'Action'), ('generate_name', 'Generate Name')], max_length=50, verbose_name='Job type'),
        ),
        migrations.AlterField(
            model_name='recurringjob',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots'), ('action', 'Action'), ('generate_name', 'Generate Name')], max_length=50, verbose_name='Job type'),
        ),
    ]
