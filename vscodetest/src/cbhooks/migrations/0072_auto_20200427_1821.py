# Generated by Django 2.2.10 on 2020-04-27 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0071_auto_20200324_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hookpoint',
            name='job_type',
            field=models.CharField(blank=True, choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('import_parameters', 'Import Parameters'), ('import_images', 'Import Images for Resource Handler'), ('import_ipam_networks', 'Import IPAM Networks'), ('servermodification', 'Server Modification'), ('deploy_blueprint', 'Deploy Blueprint'), ('install_pod', 'Install Container Object'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots'), ('action', 'Action'), ('generate_name', 'Generate Name')], max_length=50, null=True, verbose_name='Job Type'),
        ),
    ]
