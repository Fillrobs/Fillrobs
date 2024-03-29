# Generated by Django 2.2.10 on 2020-03-23 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0050_add_workspace_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='configuration_admin',
            field=models.BooleanField(default=False, help_text='Provides ability to initially deploy and configure the system, LDAP endpoints, licenses, etc.'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='workspace_creator',
            field=models.BooleanField(default=False, help_text='Provides ability to create user workspaces.'),
        ),
    ]
