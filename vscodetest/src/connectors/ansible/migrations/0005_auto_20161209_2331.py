# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0004_auto_20161209_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ansibleconf',
            name='connection_info',
            field=models.ForeignKey(blank=True, to='utilities.ConnectionInfo', help_text='Ansible Management Connection Info.', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansiblegroup',
            name='available_playbooks',
            field=models.ManyToManyField(help_text='Playbooks available to run on servers in this group.', related_name='groups_available', null=True, to='ansible.AnsiblePlaybook', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansiblegroup',
            name='cb_application',
            field=models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt.', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ansiblegroup',
            name='initialization_playbooks',
            field=models.ManyToManyField(help_text='Playbooks used to initialize servers in this group.', related_name='groups_initialized', null=True, to='ansible.AnsiblePlaybook', blank=True),
            preserve_default=True,
        ),
    ]
