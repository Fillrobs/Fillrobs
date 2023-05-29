# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0002_auto_20161004_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='openstackhandler',
            name='domain',
            field=models.CharField(help_text='Keystone authentication domain', max_length=256, null=True, verbose_name='Domain', blank=True),
            preserve_default=True,
        ),
    ]
