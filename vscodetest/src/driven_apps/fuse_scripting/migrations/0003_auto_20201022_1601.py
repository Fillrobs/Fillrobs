# Generated by Django 2.2.10 on 2020-10-22 16:01

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_scripting', '0002_auto_20201020_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptingpolicy',
            name='name',
            field=models.CharField(help_text='The user-specified name of this Scripting Policy.', max_length=255),
        ),
        migrations.AlterField(
            model_name='scriptingpolicy',
            name='provision_launch_command_template',
            field=common.fields.TemplatableField(help_text='The launch command template for this Scripting Policy.', max_length=65536),
        ),
        migrations.AlterField(
            model_name='scriptingpolicy',
            name='provision_script',
            field=common.fields.TemplatableField(help_text='The script for this Scripting Policy.', max_length=65536),
        ),
        migrations.AlterField(
            model_name='scriptingpolicy',
            name='provision_success_exit_codes',
            field=common.fields.TemplatableField(help_text='The success exit codes for this Scripting Policy.', max_length=65536),
        ),
        migrations.AlterField(
            model_name='scriptingpolicy',
            name='target_host',
            field=common.fields.TemplatableField(help_text='The target host for this Scripting Policy.', max_length=65536),
        ),
    ]
