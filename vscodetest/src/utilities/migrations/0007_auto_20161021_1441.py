# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0006_radiusutility_auth_policy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldaputility',
            name='ldap_username',
            field=models.CharField(help_text='LDAP attribute to map to username. In Active Directory, this should be <code>sAMAccountName</code>. This is case-sensitive.', max_length=50, verbose_name='Username Field'),
            preserve_default=True,
        ),
    ]
