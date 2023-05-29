# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-05 22:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IPAMNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CIDR', models.CharField(max_length=43)),
                ('real_type', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='ipam',
            name='ipam_networks',
            field=models.ManyToManyField(to='ipam.IPAMNetwork'),
        ),
    ]