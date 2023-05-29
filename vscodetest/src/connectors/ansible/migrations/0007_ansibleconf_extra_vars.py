# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0006_ansibleconf_inventory_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='ansibleconf',
            name='extra_vars',
            field=models.TextField(help_text="Extra variables to pass to Ansible's '--extra-vars' flag.", null=True, blank=True),
            preserve_default=True,
        ),
    ]
