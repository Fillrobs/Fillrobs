# Generated by Django 2.2.16 on 2021-02-22 19:01

from django.db import migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0074_auto_20210209_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobmetadata',
            name='_rendered_templates',
            field=django_extensions.db.fields.json.JSONField(blank=True, default={}, help_text='Stores all templated fields with their rendered values', null=True),
        ),
    ]
