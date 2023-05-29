# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('hyperv', '0002_hypervresourcehandler_server'),
    ]

    operations = [
        migrations.CreateModel(
            name='HyperVImage',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=1024)),
                ('vhdx_disk_path', models.CharField(max_length=1024)),
                ('total_disk_size', models.DecimalField(help_text='Total size of all disks on this image in GB', null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
            options={
                'verbose_name': 'Image',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.AddField(
            model_name='hypervresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='hyperv.HyperVImage', null=True, blank=True),
            preserve_default=True,
        ),
    ]
