# Generated by Django 2.2.10 on 2020-01-17 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0064_auto_20191118_2305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runhookinputmapping',
            name='options',
        ),
    ]