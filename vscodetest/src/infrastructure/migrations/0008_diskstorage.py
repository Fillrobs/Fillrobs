# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('resourcehandlers', '0002_auto_20161004_2121'),
        ('infrastructure', '0007_auto_20161004_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiskStorage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('real_type', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, editable=False, to='contenttypes.ContentType', null=True)),
                ('resource_handler', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='resourcehandlers.ResourceHandler', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DiskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('disk_type', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='diskstorage',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.DiskType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='disk',
            name='disk_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.DiskStorage', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customfield',
            name='type',
            field=models.CharField(max_length=6, choices=[('STR', 'String'), ('INT', 'Integer'), ('IP', 'IP Address'), ('DT', 'Date & Time'), ('TXT', 'Multi-line Text'), ('ETXT', 'Encrypted Text'), ('CODE', 'Code'), ('BOOL', 'Boolean'), ('DEC', 'Decimal'), ('NET', 'Network'), ('PWD', 'Password'), ('TUP', 'Tuple'), ('LDAP', 'LDAPUtility'), ('URL', 'URL'), ('NSXS', 'NSX Scope'), ('NSXE', 'NSX Edge'), ('STOR', 'DiskStorage')]),
            preserve_default=True,
        ),
    ]
