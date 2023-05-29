# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portalconfig',
            name='ldaps',
            field=models.ManyToManyField(help_text='LDAP domains to show on the login page for this portal. Unrestricted if none are selected.', to='utilities.LDAPUtility', verbose_name='Login LDAP Domains', blank=True),
        ),
    ]
