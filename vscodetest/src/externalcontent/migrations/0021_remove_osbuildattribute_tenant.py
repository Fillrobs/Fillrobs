# Generated by Django 2.2.16 on 2021-04-12 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0020_merge_20210226_1415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='osbuildattribute',
            name='tenant',
        ),
    ]
