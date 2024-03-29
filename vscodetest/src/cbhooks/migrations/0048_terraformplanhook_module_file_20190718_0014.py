# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-18 00:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0047_terraformstatefile_hook'),
    ]

    operations = [
        migrations.AddField(
            model_name='terraformplanhook',
            name='module_file',
            field=models.FileField(blank=True, help_text='A zip file containing Terraform plans', max_length=255, null=True, upload_to='hooks'),
        ),
        migrations.AddField(
            model_name='terraformplanhook',
            name='source_code_url',
            field=models.TextField(blank=True, help_text='Code will be fetched from here before action is run. E.g. URL (without any authentication tokens) to the raw file hosted on your github.com repository. For details \n\n\n\n\n\n<a href="/static/docs/advanced/orchestration-actions/actions.html#external-source-code"\n    target="help"\n    class="no-tooltip-affordance"\n    data-toggle="tooltip"\n    data-html="true"\n    title="Learn more in the docs <p>(new window)</p>">\n     see the docs \n    <i class="icon-help"></i>\n</a>\n.', null=True, verbose_name='URL for source code'),
        ),
        migrations.RenameField(
            model_name='terraformplanhook',
            old_name='plan_path',
            new_name='local_path',
        ),
        migrations.AlterField(
            model_name='terraformplanhook',
            name='local_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='terraformplanhook',
            name='plan_directory',
            field=models.CharField(blank=True, help_text='Optional field to add a plan directory if you are uploading a plan inside a zip file that has multiple files in it.', max_length=255, null=True),
        ),
    ]
