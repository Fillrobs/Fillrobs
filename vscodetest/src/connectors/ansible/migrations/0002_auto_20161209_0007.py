# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ansiblenode',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='ansiblenode',
            name='cb_server',
        ),
        migrations.RemoveField(
            model_name='ansiblenode',
            name='conf',
        ),
        migrations.RemoveField(
            model_name='ansiblenode',
            name='roles',
        ),
        migrations.DeleteModel(
            name='AnsibleNode',
        ),
    ]
