# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0002_serviceitem_show_on_order_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loadbalancerserviceitem',
            name='servers',
            field=models.ManyToManyField(help_text='Servers to load balance. If left blank, will load balance all servers built up to this point in the service.', related_name='load_balancers', to='servicecatalog.ProvisionServerServiceItem', blank=True),
        ),
        migrations.AlterField(
            model_name='networkserviceitem',
            name='servers',
            field=models.ManyToManyField(help_text='Servers to put on this new network when they are provisioned.', related_name='networks', to='servicecatalog.ProvisionServerServiceItem', blank=True),
        ),
        migrations.AlterField(
            model_name='provisionserverserviceitem',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='runremotescripthookserviceitem',
            name='targets',
            field=models.ManyToManyField(help_text='This script will run on all servers created by the specified service item.If no targets are selected, script will be run on all servers created by this service (at the time when the script runs)', related_name='script_hooks_to_run', to='servicecatalog.ProvisionServerServiceItem', blank=True),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='custom_field_options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='custom_fields_for_service',
            field=models.ManyToManyField(related_name='serviceblueprint_set_for_service', to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='serviceblueprint',
            name='custom_fields_for_sis',
            field=models.ManyToManyField(related_name='serviceblueprint_set_for_sis', to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='enabled_environments',
            field=models.ManyToManyField(related_name='enabled_service_items', to='infrastructure.Environment', blank=True),
        ),
    ]
