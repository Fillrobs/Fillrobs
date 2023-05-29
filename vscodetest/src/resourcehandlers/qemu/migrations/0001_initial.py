# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='QemuOSBuildAttribute',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'QEMU-KVM OS Build Attribute',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
    ]
