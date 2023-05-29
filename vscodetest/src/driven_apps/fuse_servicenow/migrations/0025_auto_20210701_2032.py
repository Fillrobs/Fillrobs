# Generated by Django 3.2.3 on 2021-07-01 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_servicenow', '0024_alter_servicenowconnectorpolicy_inputs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicenowconnectordeployment',
            name='vra_policy',
        ),
        migrations.AddField(
            model_name='servicenowconnectordeployment',
            name='_child_policy_href',
            field=models.TextField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servicenowconnectordeployment',
            name='servicenow_deployment_sys_id',
            field=models.CharField(default='sys_id', help_text='The sys_id in the ServiceNow instance referenced in the policy which represents this deployment.', max_length=255),
            preserve_default=False,
        ),
    ]