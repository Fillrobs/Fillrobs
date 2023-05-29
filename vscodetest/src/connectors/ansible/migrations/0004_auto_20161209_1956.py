# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0003_auto_20161209_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='ansiblegroup',
            name='available_playbooks',
            field=models.ManyToManyField(related_name='groups_available', null=True, to='ansible.AnsiblePlaybook', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansiblegroup',
            name='initialization_playbooks',
            field=models.ManyToManyField(related_name='groups_initialized', null=True, to='ansible.AnsiblePlaybook', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansibleplaybook',
            name='name',
            field=models.CharField(help_text='The name this playbook file.', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansibleplaybook',
            name='path',
            field=models.CharField(help_text='The full path to this playbook on the management server.', max_length=255),
            preserve_default=True,
        ),
    ]
