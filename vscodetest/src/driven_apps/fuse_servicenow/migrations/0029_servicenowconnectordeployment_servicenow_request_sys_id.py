# Generated by Django 3.2.3 on 2021-08-03 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_servicenow', '0028_alter_servicenowconnectorpolicy_child_policy_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenowconnectordeployment',
            name='servicenow_request_sys_id',
            field=models.CharField(blank=True, default='', help_text='The sys_id in the ServiceNow request that executed this deployment.', max_length=255),
        ),
    ]
