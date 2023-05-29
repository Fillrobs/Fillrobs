# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-16 19:19
from __future__ import unicode_literals

from django.db import migrations


def set_blueprint_on_orders(apps, schema_editor):
    """
    Set the new blueprint attribute on any existing orders where we can, namely
    those that have an ISOI. This will help with allowing edit of those existing
    orders, which requires the blueprint attribute.
    """
    Order = apps.get_model('orders', 'Order')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    isoi_ct = ContentType.objects.filter(
        app_label="orders", model="installserviceorderitem").first()
    # If this ContentType doesn't exist, we can't do anything, (probably?)
    # because this migration is running during a fresh install
    if not isoi_ct:
        return

    for order in Order.objects.all():
        isoi = order.orderitem_set.filter(real_type=isoi_ct).first()
        if isoi:
            order.blueprint = isoi.installserviceorderitem.blueprint
            order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_blueprint'),
    ]

    operations = [
        migrations.RunPython(set_blueprint_on_orders),
    ]
