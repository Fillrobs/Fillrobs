# Generated by Django 2.2.16 on 2021-03-10 23:17

import cb_secrets.fields
import common.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0022_auto_20210219_1515'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('utilities', '0100_merge_20210303_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSHKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('global_id', models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID')),
                ('name', models.CharField(help_text='Label for this SSH Key', max_length=80)),
                ('real_type', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
                ('resource_handler', models.ForeignKey(blank=True, help_text='Optional resource handler to which this SSH key applies.If not set, then the SSH Key applies globally.', null=True, on_delete=django.db.models.deletion.CASCADE, to='resourcehandlers.ResourceHandler', verbose_name='Resource Handler')),
            ],
            options={
                'verbose_name': 'SSH Key',
            },
            bases=(common.mixins.ModelRBACMixin, models.Model),
        ),
        migrations.CreateModel(
            name='StoredSSHKey',
            fields=[
                ('sshkey_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='utilities.SSHKey')),
                ('private_key', cb_secrets.fields.EncryptedTextField(help_text='SSH Private Key Data in PEM Format')),
            ],
            options={
                'verbose_name': 'Stored SSH Key',
                'abstract': False,
            },
            bases=('utilities.sshkey',),
        ),
    ]
