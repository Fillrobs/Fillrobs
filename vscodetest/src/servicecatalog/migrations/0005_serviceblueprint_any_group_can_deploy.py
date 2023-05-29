# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0004_serviceblueprint_create_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='any_group_can_deploy',
            field=models.BooleanField(default=False, help_text='Allow any group to order the Blueprint, rather than only giving deploy permissions to specific groups.'),
            preserve_default=True,
        ),
    ]
