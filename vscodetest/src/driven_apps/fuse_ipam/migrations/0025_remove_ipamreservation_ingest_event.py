# Generated by Django 3.2.3 on 2021-06-29 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_ipam', '0024_auto_20210618_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ipamreservation',
            name='ingest_event',
        ),
    ]