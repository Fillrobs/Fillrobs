# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('accounts', '0002_auto_20160829_2059'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license_file', models.FileField(null=1, upload_to='/home/david/var/opt/cloudbolt/filefields/licenses/', blank=1)),
                ('license_string', models.CharField(max_length=2048, null=1, blank=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LicensePool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, blank=True)),
                ('type', models.CharField(max_length=10, choices=[('FILE', 'File'), ('STRING', 'String'), ('NONE', 'No license material')])),
                ('applications', models.ManyToManyField(to='externalcontent.Application', null=True, blank=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.Group', null=True)),
                ('os_builds', models.ManyToManyField(to='externalcontent.OSBuild', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='license',
            name='license_pool',
            field=models.ForeignKey(to='licenses.LicensePool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='license',
            name='server',
            field=models.ForeignKey(blank=True, to='infrastructure.Server', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
