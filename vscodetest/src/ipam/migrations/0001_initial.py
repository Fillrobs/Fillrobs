# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cb_secrets.fields
import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IPAM',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=50, verbose_name='IP address')),
                ('port', models.IntegerField(default=443, help_text='Port used to connect to this ip manager', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(default='https', help_text='Protocol used to connect to this ip manager', max_length=10, choices=[('http', 'http'), ('https', 'https')])),
                ('serviceaccount', models.CharField(help_text='Username of account authorized to run commands on this ip manager', max_length=250, verbose_name='Account username')),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(verbose_name='Account password')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IPAMTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name of the ip management technology (ex. Infoblox)')),
                ('version', models.CharField(max_length=20, verbose_name='Version of the resource technology')),
                ('modulename', models.CharField(max_length=50, verbose_name='Python module for interacting with this version of this ip management technology.', blank=1)),
            ],
            options={
                'verbose_name_plural': 'IPAM technologies',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ipam',
            name='ipam_technology',
            field=models.ForeignKey(to='ipam.IPAMTechnology', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ipam',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
