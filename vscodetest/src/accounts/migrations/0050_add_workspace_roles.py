# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop)
    ]

    dependencies = [
        ('accounts', '0049_auto_20200320_1823'),
        ('jobengine', '0002_jobengineworker_max_concurrency'),
        ('utilities', '0082_globalpreferences_auto_login_sso'),
        ('jobs', '0038_auto_20200306_1551'),
    ]
