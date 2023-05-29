# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-29 21:22
from __future__ import unicode_literals

from django.db import migrations
from utilities.fontawesome4to5 import convert_fontawesome_in_string
from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


def update_fa_classes(apps, schema_editor):
    """
    Update user-generated action classes from Font Awesome v4 icons to v5
    """
    logger.info('Updating Font Awesome classes on all actions from v4 icons to v5')

    ResourceAction = apps.get_model('cbhooks', 'ResourceAction')
    ServerAction = apps.get_model('cbhooks', 'ServerAction')
    for model in [ResourceAction, ServerAction]:
        for action in model.objects.all():
            new_classes = convert_fontawesome_in_string(action.extra_classes)
            if new_classes != action.extra_classes:
                logger.info('Updating Font Awesome classes on {}'.format(action))
                action.extra_classes = new_classes
                action.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0043_dblock'),
    ]

    operations = [
        migrations.RunPython(update_fa_classes),
    ]
