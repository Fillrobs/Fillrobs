# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 14:25
from __future__ import unicode_literals

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0004_remove_portalconfig_topnav_search_bg_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='portalconfig',
            name='footer_logo',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Logo shown in the page footer.  64px tall is optimal.', null=True, upload_to='branding/'),
        ),
        migrations.AddField(
            model_name='portalconfig',
            name='header_logo',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Logo shown in the top navigation menu.  108px tall is optimal.', null=True, upload_to='branding/'),
        ),
        migrations.AddField(
            model_name='portalconfig',
            name='is_default',
            field=models.BooleanField(default=False, help_text='Making this instance the default will remove the property from all other instances.'),
        ),
        migrations.AddField(
            model_name='portalconfig',
            name='loading_image',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Image shown when pages are loading.  244px tall is optimal.', null=True, upload_to='branding/'),
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='custom_banner',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Logo shown in as banner above the navigation menu.  Max 80px tall is optimal.', null=True, upload_to='branding/'),
        ),
        migrations.AlterField(
            model_name='portalconfig',
            name='name',
            field=models.CharField(help_text='The name of the portal. If this portal is in use, this field will be used as the title shown to users throughout the product.', max_length=50),
        ),
    ]