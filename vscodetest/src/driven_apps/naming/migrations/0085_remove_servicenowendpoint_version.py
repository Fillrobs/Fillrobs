# Generated by Django 3.2.3 on 2021-07-09 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0084_alter_servicenowendpoint_version'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicenowendpoint',
            name='version',
        ),
    ]