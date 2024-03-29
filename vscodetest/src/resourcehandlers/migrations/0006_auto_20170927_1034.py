# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0005_auto_20170721_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcehandler',
            name='ignore_vm_folders',
            field=models.TextField(blank=True, help_text='A comma separated list of the folders of VMs to exclude during VM synchronization. These folders names are regular expressions. Example: <code>Secure Servers.*, AD Servers</code>. Specifying this field will slow down VM synchronization jobs for some technologies (ex. VMware). If a rule is introduced which ignores a VM already managed by CloudBolt, that VM will be marked historical in CloudBolt after the next sync.', null=True),
        ),
        migrations.AlterField(
            model_name='resourcehandler',
            name='ignore_vm_names',
            field=models.TextField(blank=True, help_text='A comma separated list of the names of VMs to exclude during VM synchronization. These names are regular expressions, and any whitespace surrounding each rule will be ignored. Example: <code> proddb.*, joetest1, .*qalab.*</code>. If a rule is introduced which ignores a VM already managed by CloudBolt, that VM will be marked historical in CloudBolt after the next sync.', null=True),
        ),
    ]
