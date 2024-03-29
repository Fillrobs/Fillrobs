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
    logger.info(
        'Updating Font Awesome classes on all actions from v4 icons to v5')

    ResourceType = apps.get_model('resources', 'ResourceType')
    for restype in ResourceType.objects.all():
        new_classes = convert_fontawesome_in_string(restype.icon)
        if new_classes != restype.icon:
            logger.info(
                'Updating Font Awesome classes on {}'.format(restype))
            restype.icon = new_classes
            restype.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0007_auto_20180607_1305'),
    ]

    operations = [
        migrations.RunPython(update_fa_classes),
    ]
