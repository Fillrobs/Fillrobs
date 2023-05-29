# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-27 21:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0006_billinglineitem'),
        ('aws', '0007_ebs_volume_type_options_and_more_20180606_1654'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSBillingLineItem',
            fields=[
                ('billinglineitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='costs.BillingLineItem')),
                ('usage_type', models.CharField(max_length=255)),
                ('product_name', models.CharField(max_length=255)),
            ],
            bases=('costs.billinglineitem',),
        ),
    ]
