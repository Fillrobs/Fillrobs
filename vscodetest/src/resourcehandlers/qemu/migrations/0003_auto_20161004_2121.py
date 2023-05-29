# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qemu', '0002_qemuresourcehandler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qemuresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='qemu.QemuOSBuildAttribute', blank=True),
        ),
    ]
