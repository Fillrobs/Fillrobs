# Generated by Django 2.2.10 on 2020-09-04 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_ipam', '0004_auto_20200901_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='infobloxipampolicy',
            name='fixed_address_record_template',
        ),
        migrations.RemoveField(
            model_name='infobloxipampolicy',
            name='network_view',
        ),
    ]