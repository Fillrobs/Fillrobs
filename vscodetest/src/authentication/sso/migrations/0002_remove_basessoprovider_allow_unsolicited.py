# Generated by Django 2.2.10 on 2020-03-11 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basessoprovider',
            name='allow_unsolicited',
        ),
    ]
