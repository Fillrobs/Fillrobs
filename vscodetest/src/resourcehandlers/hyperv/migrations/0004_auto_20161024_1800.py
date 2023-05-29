# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hyperv', '0003_auto_20161017_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='hypervresourcehandler',
            name='images_dir',
            field=models.CharField(default='C:\\exports', help_text='Directory on the Hyper-V server where VM images are stored.', max_length=1024, verbose_name='Images Directory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='hypervresourcehandler',
            name='server',
            field=models.ForeignKey(to='infrastructure.Server', help_text='Choose a server running a Hyper-V Manager.', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
