# Generated by Django 2.2.16 on 2021-03-31 03:01

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields.json
import driven_apps.common.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0060_role_group_types'),
        ('fuse_servicenow', '0013_servicenowconnectorpolicy_inputs'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceNowConnectorCatalogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The user-specified name of this ServiceNow Connector Catalog Item.', max_length=255)),
                ('description', models.TextField(blank=True, help_text='The description text for this ServiceNow Connector Catalog Item.', null=True)),
                ('catalog', models.TextField(help_text='The catalog sys_id in ServiceNow for this ServiceNow Connector Catalog Item.')),
                ('category', models.TextField(help_text='The category sys_id from the specified catalog in ServiceNow for this ServiceNow Connector Catalog Item.')),
                ('inputs', django_extensions.db.fields.json.JSONField(default=dict, help_text='A list of ServiceNow Connector Catalog Item inputs {"name": <string>, "label": <string>, "required": <boolean>} to be created on the catalog item in ServiceNow.')),
                ('policy', models.ForeignKey(help_text='ServiceNow Connector Policy for this ServiceNow Connector Catalog Item.', on_delete=django.db.models.deletion.PROTECT, to='fuse_servicenow.ServiceNowConnectorPolicy')),
                ('workspace', models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group')),
            ],
            options={
                'verbose_name_plural': 'ServiceNow Connector Catalog Items',
                'db_table': 'servicenow_connector_catalog_items',
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=(models.Model, driven_apps.common.mixins.RoleBasedHalFilteringMixin),
        ),
    ]