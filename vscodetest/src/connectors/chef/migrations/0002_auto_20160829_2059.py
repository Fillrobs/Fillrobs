# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0001_initial'),
        ('chef', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chefrole',
            name='cb_application',
            field=models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chefrole',
            name='chef_conf',
            field=models.ForeignKey(to='chef.ChefConf', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
