# Generated by Django 3.2.3 on 2021-06-18 16:05

from django.db import migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_servicenow', '0023_auto_20210615_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicenowconnectorpolicy',
            name='inputs',
            field=django_extensions.db.fields.json.JSONField(default=dict, help_text='A list of ServiceNow Connector Catalog Item inputs {"name": <string>, "label": <string>, "required": <boolean>} to be created on the catalog item in ServiceNow.'),
        ),
    ]