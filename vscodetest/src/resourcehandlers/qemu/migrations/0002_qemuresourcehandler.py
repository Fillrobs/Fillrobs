# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('resourcehandlers', '0001_initial'),
        ('qemu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QemuResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('template_name_pattern', models.CharField(default='-tmpl', help_text='Regular expression to designate which domains to treat as templates. All others will be treated as VMs.', max_length=100)),
                ('clone_tmpl_timeout', models.IntegerField(default=60)),
                ('os_build_attributes', models.ManyToManyField(to='qemu.QemuOSBuildAttribute', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'QEMU-KVM resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
