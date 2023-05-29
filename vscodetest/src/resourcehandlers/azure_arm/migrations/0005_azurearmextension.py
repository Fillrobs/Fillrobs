# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0004_azurearmdisk'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureARMExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('arm_server', models.ForeignKey(related_name='extensions', to='azure_arm.AzureARMServerInfo', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
