# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cscv', '0001_initial'),
        ('services', '0001_initial'),
        ('jobs', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='hookparameters',
            name='services',
            field=models.ManyToManyField(to='services.Service', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='functionaltestparameters',
            name='cittests',
            field=models.ManyToManyField(help_text='Test(s) to run', to='cscv.CITTest', null=True),
            preserve_default=True,
        ),
    ]
