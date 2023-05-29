# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0005_serviceblueprint_any_group_can_deploy'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serviceblueprintgrouppermissions',
            options={'verbose_name': 'Blueprint group permission', 'verbose_name_plural': 'Blueprint group permissions'},
        ),
        migrations.AlterField(
            model_name='runremotescripthookserviceitem',
            name='targets',
            field=models.ManyToManyField(help_text='This script will run on all servers created by the specified blueprint item.If no targets are selected, script will be run on all servers created by this blueprint (at the time when the script runs)', related_name='script_hooks_to_run', to='servicecatalog.ProvisionServerServiceItem', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='deploy_seq',
            field=models.IntegerField(help_text='Order in which blueprint items of a service will be deployed.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='description',
            field=models.TextField(help_text='Optional detailed description about this blueprint item for end users.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='name',
            field=models.CharField(help_text='Optional name to identify this blueprint item to end users.', max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
    ]
