# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrationengines', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orchestrationflow',
            name='environments',
            field=models.ManyToManyField(related_name='flows', to='infrastructure.Environment', blank=True),
        ),
    ]
