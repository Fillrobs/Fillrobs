# Generated by Django 2.2.16 on 2020-10-28 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_tower', '0004_auto_20201028_1613'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ansibletowerpolicy',
            options={'ordering': ['id'], 'verbose_name': 'Ansible Tower Policy', 'verbose_name_plural': 'Ansible Tower Policies'},
        ),
    ]