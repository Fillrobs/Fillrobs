# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-26 14:52
from __future__ import unicode_literals

from django.db import migrations, models
from autoslug import AutoSlugField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', AutoSlugField(editable=False, populate_from='name', unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('subject', models.CharField(default='', max_length=1024)),
                ('from_address', models.CharField(blank=True, help_text="Specify as: 'Full Name &lt;email@address>'<br/>Defaults to: 'no-reply@site.domain'", max_length=320)),
                ('body', models.TextField(default='')),
                ('text_body', models.TextField(blank=True, default='', help_text='If provided, render as the plain-text body')),
                ('is_renamable', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'email template',
                'verbose_name_plural': 'email templates',
            },
        ),
    ]