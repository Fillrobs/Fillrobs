# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-19 21:05
from __future__ import unicode_literals

from django.db import migrations
from infrastructure.models import IMMUTABLE_SERVER_ATTRIBUTES, OPTIONALLY_MUTABLE_SERVER_ATTRIBUTES


def set_bidirectional_sync_on_tags(apps, schema_editor):
    """
    Sets the boolean value for bidirectional_sync on existing TaggableAttribute instances
    """
    TaggableAttribute = apps.get_model('tags', 'TaggableAttribute')
    for ta in TaggableAttribute.objects.all():
        if ta.attribute in IMMUTABLE_SERVER_ATTRIBUTES or ta.attribute in OPTIONALLY_MUTABLE_SERVER_ATTRIBUTES:
            ta.bidirectional_sync = False
        else:
            ta.bidirectional_sync = True
        ta.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0009_taggableattribute_bidirectional_sync'),
    ]

    operations = [
        migrations.RunPython(set_bidirectional_sync_on_tags)
    ]