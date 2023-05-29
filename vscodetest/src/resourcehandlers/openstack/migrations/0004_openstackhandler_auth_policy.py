# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0003_openstackhandler_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='openstackhandler',
            name='auth_policy',
            field=models.CharField(default='A2I2C2', max_length=50, verbose_name='Authentication Policy', choices=[('A2I2C2', 'Auth Policy version 2.0; Identity v2; Compute v2; Public URL'), ('A3I3C2', 'Auth Policy version 3; Identity v3; Compute v2; Public URL'), ('A3I3C3', 'Auth Policy version 3; Identity v3; Compute v3; Public URL')]),
            preserve_default=True,
        ),
    ]
