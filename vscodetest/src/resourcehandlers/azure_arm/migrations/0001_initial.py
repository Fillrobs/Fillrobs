# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AzureARMAvailableImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('publisher', models.CharField(max_length=255)),
                ('offer', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('azure_image_name', models.CharField(max_length=255, blank=True)),
                ('guest_os', models.CharField(max_length=255, blank=True)),
                ('template_name', models.CharField(max_length=255, blank=True)),
                ('total_disk_size', models.DecimalField(help_text='Total size of all disks on this image in GB', null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
