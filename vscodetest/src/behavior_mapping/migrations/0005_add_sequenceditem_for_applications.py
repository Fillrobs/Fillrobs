# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-31 01:52
from __future__ import unicode_literals

from django.db import migrations, models


def add_sequenced_item_for_applications(apps, schema_editor):
    SequencedItem = apps.get_model('behavior_mapping', 'SequencedItem')
    if not SequencedItem.objects.exists():
        # No sequenced items exist, they're probably all about to be created
        return
    if SequencedItem.objects.filter(other_name='applications').exists():
        # It already exists, do nothing
        return
    if SequencedItem.objects.filter(other_name='os_build').exists():
        # Put applications after os_build
        osb_seq = SequencedItem.objects.get(other_name='os_build').seq
        for item in SequencedItem.objects.filter(seq__gt=osb_seq):
            item.seq = item.seq + 1
            item.save()
        SequencedItem.objects.create(
            other_name='applications',
            other_label='Applications',
            seq=osb_seq + 1)
    else:
        # Put applications at the end
        last_seq = SequencedItem.objects.all().aggregate(models.Max('seq'))
        SequencedItem.objects.create(
            other_name='applications',
            other_label='Applications',
            seq=last_seq + 1)


class Migration(migrations.Migration):

    dependencies = [
        ('behavior_mapping', '0004_auto_20161004_2121'),
    ]

    operations = [
        migrations.RunPython(add_sequenced_item_for_applications),
    ]
