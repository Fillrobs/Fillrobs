# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('externalcontent', '0001_initial'),
        ('chef', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='chefnode',
            name='cb_server',
            field=models.OneToOneField(related_name='chef_node', null=True, blank=True, to='infrastructure.Server', on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chefnode',
            name='conf',
            field=models.ForeignKey(related_name='nodes', to='chef.ChefConf', help_text='The Chef Conf that manages this Chef Node.', on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chefnode',
            name='cookbooks',
            field=models.ManyToManyField(help_text='Cookbooks to be installed on this node', to='chef.ChefCookbook'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chefnode',
            name='roles',
            field=models.ManyToManyField(help_text='Roles to be installed on this node', to='chef.ChefRole'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='chefnode',
            unique_together=set([('node_name', 'conf')]),
        ),
        migrations.AddField(
            model_name='chefcookbook',
            name='cb_application',
            field=models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chefcookbook',
            name='chef_conf',
            field=models.ForeignKey(to='chef.ChefConf', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
