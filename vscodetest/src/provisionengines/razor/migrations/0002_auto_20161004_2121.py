# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('razor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='razorserver',
            name='repositories',
            field=models.ManyToManyField(to='razor.RazorRepository', blank=True),
        ),
    ]
