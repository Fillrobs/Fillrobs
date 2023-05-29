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
            name='ContainerOrchestrator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('ip', models.CharField(max_length=50, verbose_name='IP address', validators=[common.validators.validate_domain_or_ip])),
                ('port', models.IntegerField(default=443, help_text='Port used to connect to this resource handler', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(default='http', help_text='Protocol used to connect to this resource handler', max_length=10, choices=[('http', 'http'), ('https', 'https')])),
                ('serviceaccount', models.CharField(help_text='Username of account authorized to run commands on this resource handler', max_length=250, verbose_name='Account username')),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(verbose_name='Account password')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContainerOrchestratorTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Resource technologies',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='containerorchestrator',
            name='container_technology',
            field=models.ForeignKey(to='containerorchestrators.ContainerOrchestratorTechnology', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='containerorchestrator',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
