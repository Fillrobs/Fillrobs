# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0006_customfield_show_as_attribute'),
        ('hyperv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hypervresourcehandler',
            name='server',
            field=models.ForeignKey(to='infrastructure.Server', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
