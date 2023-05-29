# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_url', models.CharField(max_length=1000)),
                ('page_title', models.CharField(max_length=250, null=True, blank=True)),
                ('added', models.DateTimeField(default=datetime.datetime.now)),
                ('profile', models.ForeignKey(to='accounts.UserProfile', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['added'],
            },
            bases=(models.Model,),
        ),
    ]
