# Generated by Django 2.2.12 on 2020-07-06 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0031_vra8endpoint_credential'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobmetadata',
            options={'ordering': ['-_end_time'], 'verbose_name': 'job metadata record', 'verbose_name_plural': 'job metadata records'},
        ),
    ]
