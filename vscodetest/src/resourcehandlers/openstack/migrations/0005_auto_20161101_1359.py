# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0004_openstackhandler_auth_policy'),
    ]

    operations = [
        migrations.AddField(
            model_name='openstackhandler',
            name='project_id',
            field=models.CharField(help_text='Keystone authentication project id. Required for version 3', max_length=100, null=True, verbose_name='Project ID', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='openstackhandler',
            name='auth_policy',
            field=models.CharField(default='A2I2C2', max_length=50, verbose_name='Authentication Policy', choices=[('A2I2C2', 'Auth Policy v2; Identity v2; Compute v2; Public URL'), ('A3I3C2', 'Auth Policy v3; Identity v3; Compute v2; Public URL')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='openstackhandler',
            name='domain',
            field=models.CharField(help_text='Keystone authentication domain. Required for version 3', max_length=256, null=True, verbose_name='Domain', blank=True),
            preserve_default=True,
        ),
    ]
