# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields
import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the portal', unique=True, max_length=50)),
                ('domain', models.CharField(help_text='Domain or IP used to access this CloudBolt portal. Used for determining the portal and for generating links.', max_length=255, verbose_name='Domain/IP', validators=[common.validators.validate_domain_or_ip])),
                ('security_bg_color', common.fields.ColorPickerField(help_text='Background color of security message (see Misc Settings)', max_length=7, null=True, verbose_name='Security background', blank=True)),
                ('security_text_color', common.fields.ColorPickerField(help_text='Color of security message text', max_length=7, null=True, verbose_name='Security text', blank=True)),
                ('custom_banner', models.ImageField(default='', upload_to='branding/', blank=True, help_text='Logo shown in the banner area.  Max 80px tall is optimal.', null=True)),
                ('banner_bg_color', common.fields.ColorPickerField(help_text='Background color of banner area', max_length=7, null=True, verbose_name='Banner background', blank=True)),
                ('topnav_bg_color', common.fields.ColorPickerField(help_text='Background color of top nav menu bar', max_length=7, null=True, verbose_name='Top menu background', blank=True)),
                ('topnav_text_color', common.fields.ColorPickerField(help_text='Color of top nav text', max_length=7, null=True, verbose_name='Top menu text', blank=True)),
                ('topnav_hover_bg_color', common.fields.ColorPickerField(help_text='Hover color of top menu items. Leave blank to automatically derive this from your top nav menu background color.', max_length=7, null=True, verbose_name='Top menu hover', blank=True)),
                ('topnav_active_bg_color', common.fields.ColorPickerField(help_text='Color of the active top menu item. Leave blank to automatically derive this from your top nav menu background color.', max_length=7, null=True, verbose_name='Active top menu item', blank=True)),
                ('topnav_search_bg_color', common.fields.ColorPickerField(help_text='Background color of top menu search field. Leave blank to automatically derive this from your top nav menu background color.', max_length=7, null=True, verbose_name='Top menu search', blank=True)),
                ('footer_bg_color', common.fields.ColorPickerField(help_text='Background color of footer section', max_length=7, null=True, verbose_name='Footer background', blank=True)),
                ('footer_text_color', common.fields.ColorPickerField(help_text='Color of footer text', max_length=7, null=True, verbose_name='Footer text', blank=True)),
                ('content_bg_color', common.fields.ColorPickerField(help_text='Background color of content section', max_length=7, null=True, verbose_name='Content background', blank=True)),
                ('content_text_color', common.fields.ColorPickerField(help_text='Color of content text', max_length=7, null=True, verbose_name='Content text', blank=True)),
                ('heading_text_color', common.fields.ColorPickerField(help_text='Color of content headings', max_length=7, null=True, verbose_name='Heading text', blank=True)),
                ('tooltip_bg_color', common.fields.ColorPickerField(help_text='Background color of tooltips', max_length=7, null=True, verbose_name='Tooltip background', blank=True)),
                ('tooltip_text_color', common.fields.ColorPickerField(help_text='Color of tooltip text', max_length=7, null=True, verbose_name='Tooltip text', blank=True)),
                ('ldaps', models.ManyToManyField(help_text='LDAP domains to show on the login page for this portal. Unrestricted if none are selected.', to='utilities.LDAPUtility', null=True, verbose_name='Login LDAP Domains', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
