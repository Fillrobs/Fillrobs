# Generated by Django 2.2.10 on 2020-09-14 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0089_auto_20200727_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='globalpreferences',
            name='run_guided_setup',
        ),
    ]