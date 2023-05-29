# Generated by Django 2.2.16 on 2020-11-24 13:24

from django.db import migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_scripting', '0007_scriptingdeployment_archived'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scriptingdeployment',
            name='details',
        ),
        migrations.AddField(
            model_name='scriptingdeployment',
            name='deprovisioning_details',
            field=django_extensions.db.fields.json.JSONField(blank=True, default=dict, help_text='Deprovisioning Details', null=True),
        ),
        migrations.AddField(
            model_name='scriptingdeployment',
            name='provisioning_details',
            field=django_extensions.db.fields.json.JSONField(blank=True, default=dict, help_text='Provisioning Details', null=True),
        ),
    ]
