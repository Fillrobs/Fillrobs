# Generated by Django 2.2.16 on 2020-10-17 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0045_auto_20200825_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('import_parameters', 'Import Parameters'), ('import_images', 'Import Images for Resource Handler'), ('import_ipam_networks', 'Import IPAM Networks'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Container Object'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots'), ('action', 'Action'), ('run_policy_action', 'Run Policy Action'), ('generate_name', 'Generate Name'), ('add_ms_ad', 'Add MS AD'), ('remove_ms_ad', 'Remove MS AD'), ('update_ms_ad', 'Update MS AD'), ('apply_personality', 'Apply Personality')], max_length=50, verbose_name='Job type'),
        ),
        migrations.AlterField(
            model_name='recurringjob',
            name='type',
            field=models.CharField(choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('import_parameters', 'Import Parameters'), ('import_images', 'Import Images for Resource Handler'), ('import_ipam_networks', 'Import IPAM Networks'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Container Object'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots'), ('action', 'Action'), ('run_policy_action', 'Run Policy Action'), ('generate_name', 'Generate Name'), ('add_ms_ad', 'Add MS AD'), ('remove_ms_ad', 'Remove MS AD'), ('update_ms_ad', 'Update MS AD'), ('apply_personality', 'Apply Personality')], max_length=50, verbose_name='Job type'),
        ),
    ]
