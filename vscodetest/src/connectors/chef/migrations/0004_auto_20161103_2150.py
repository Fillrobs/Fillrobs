# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chef', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chefconf',
            name='hostname',
            field=models.CharField(help_text="Chef server's hostname or IP.  For hosted Chef, this should be set to 'api.chef.io'", max_length=255),
            preserve_default=True,
        ),
    ]
