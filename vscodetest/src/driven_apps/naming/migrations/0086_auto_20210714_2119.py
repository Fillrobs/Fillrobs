# Generated by Django 3.2.3 on 2021-07-14 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0085_remove_servicenowendpoint_version'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vra7endpoint',
            name='vra_version',
        ),
        migrations.RemoveField(
            model_name='vra8endpoint',
            name='vra_version',
        ),
    ]