# Generated by Django 3.2.5 on 2021-10-22 00:01

from django.db import migrations
from django.db.models import Q

class Migration(migrations.Migration):

    def _set_workspace_creator_and_configuration_admin_to_super_admin(apps, schema_editor):
        """
        To converge these historically OneFuse roles with the Super Admin Global Role,
        make any User with either now be a Super Admin.
        Note: Configuration Admin was added after the file was created, which is why its
        name only includes Workspace Creator
        """

        UserProfile = apps.get_model('accounts', 'UserProfile')
        UserProfile.objects.filter(Q(workspace_creator=True) | Q(configuration_admin=True)).update(super_admin=True)

    dependencies = [
        ('accounts', '0061_userprofile_legal_notice_seen'),
    ]

    operations = [
        migrations.RunPython(_set_workspace_creator_and_configuration_admin_to_super_admin, migrations.RunPython.noop)
    ]
