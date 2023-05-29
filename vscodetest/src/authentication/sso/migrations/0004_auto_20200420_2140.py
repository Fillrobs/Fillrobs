# Generated by Django 2.2.10 on 2020-04-20 21:40

import authentication.utils
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0003_auto_20200417_2350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basessoprovider',
            name='metadata_source',
        ),
        migrations.AlterField(
            model_name='basessoprovider',
            name='metadata_file',
            field=models.FileField(blank=True, null=True, storage=authentication.utils.ProservSamlFileSystemStorage(), upload_to=authentication.utils.ProservSamlFileSystemStorage.get_file_path_for_instance, verbose_name='IdP Metadata'),
        ),
        migrations.AlterField(
            model_name='basessoprovider',
            name='private_key_file',
            field=models.FileField(blank=True, help_text='If not provided, a Private Key will be generated.', null=True, storage=authentication.utils.ProservSamlFileSystemStorage(private=True), upload_to=authentication.utils.ProservSamlFileSystemStorage.get_file_path_for_instance, verbose_name='Private Key'),
        ),
        migrations.AlterField(
            model_name='basessoprovider',
            name='public_key_file',
            field=models.FileField(blank=True, help_text='If not provided, a Public Key will be generated.', null=True, storage=authentication.utils.ProservSamlFileSystemStorage(), upload_to=authentication.utils.ProservSamlFileSystemStorage.get_file_path_for_instance, verbose_name='Public Key'),
        ),
    ]
