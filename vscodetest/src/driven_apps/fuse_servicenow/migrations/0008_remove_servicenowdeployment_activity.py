# Generated by Django 2.2.16 on 2021-02-16 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_servicenow', '0007_servicenowcmdbpolicy_update_template'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicenowdeployment',
            name='activity',
        ),
    ]
