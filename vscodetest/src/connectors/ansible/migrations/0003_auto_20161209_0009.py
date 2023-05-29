# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0002_auto_20161209_0007'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnsiblePlaybook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name this Playbook to be displayed in CloudBolt.', max_length=255)),
                ('path', models.CharField(help_text='The path to this Playbook on the management server.', max_length=255)),
                ('conf', models.ForeignKey(related_name='playbooks', to='ansible.AnsibleConf', help_text='The Ansible Conf that manages this Ansible Node.', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ansiblegroup',
            name='initialization_playbooks',
            field=models.ManyToManyField(to='ansible.AnsiblePlaybook', null=True, blank=True),
            preserve_default=True,
        ),
    ]
