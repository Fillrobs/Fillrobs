# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-27 23:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0048_auto_20181218_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='default_addressing_scheme',
            field=models.CharField(choices=[('IPV4', 'IPv4'), ('IPV6', 'IPv6')], default='IPV4', help_text='Controls whether to use the IPv4 or Ipv6 address for a Server, when both are known.', max_length=5, verbose_name='Default Addressing Scheme'),
        ),
    ]