# Generated by Django 2.2.10 on 2020-02-11 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0045_auto_20191017_0101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='armstorageaccount',
            name='environment',
        ),
        migrations.RemoveField(
            model_name='armstorageaccount',
            name='handler',
        ),
        migrations.RemoveField(
            model_name='armstorageaccount',
            name='resource_group',
        ),
        migrations.DeleteModel(
            name='ARMResourceGroup',
        ),
        migrations.DeleteModel(
            name='ARMStorageAccount',
        ),
    ]