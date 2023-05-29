# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet_ent', '0003_remove_peconf_master_server'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pereport',
            options={'verbose_name': 'PE Report'},
        ),
    ]
