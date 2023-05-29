# -*- coding: utf-8 -*-
"""
No-op migrtion to change help text on a few fields.
"""
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0002_auto_20161004_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portalconfig',
            name='footer_bg_color',
            field=common.fields.ColorPickerField(help_text='Background color of footer section. Leave blank to automatically derive this from your <b>top nav menu background color</b>.', max_length=7, null=True, verbose_name='Footer background', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='security_bg_color',
            field=common.fields.ColorPickerField(help_text='Background color of security message (see Misc Settings). Leave blank to automatically derive this from your <b>content background color</b>.', max_length=7, null=True, verbose_name='Security background', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='security_text_color',
            field=common.fields.ColorPickerField(help_text='Color of security message text. Leave blank to automatically derive this from your <b>content text color</b>.', max_length=7, null=True, verbose_name='Security text', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='topnav_active_bg_color',
            field=common.fields.ColorPickerField(help_text='Color of the active top menu item. Leave blank to automatically derive this from your <b>top nav menu background color</b>.', max_length=7, null=True, verbose_name='Active top menu item', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='topnav_hover_bg_color',
            field=common.fields.ColorPickerField(help_text='Hover color of top menu items. Leave blank to automatically derive this from your <b>top nav menu background color</b>.', max_length=7, null=True, verbose_name='Top menu hover', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='topnav_search_bg_color',
            field=common.fields.ColorPickerField(help_text='Background color of top menu search field. Leave blank to automatically derive this from your <b>top nav menu background color</b>.', max_length=7, null=True, verbose_name='Top menu search', blank=True),
            preserve_default=True,
        ),
    ]
