# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('orders', '0002_auto_20160829_2059'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cbhooks', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('orchestrationengines', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('servicecatalog', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceaction',
            name='blueprints',
            field=models.ManyToManyField(help_text='Blueprints that this action applies to. If none are selected, it will apply to all.', to='servicecatalog.ServiceBlueprint', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serviceaction',
            name='hook',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serviceaction',
            name='input_mappings',
            field=models.ManyToManyField(to='cbhooks.RunHookInputMapping'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serveraction',
            name='hook',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serveraction',
            name='input_mappings',
            field=models.ManyToManyField(to='cbhooks.RunHookInputMapping'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runhookinputmapping',
            name='default_value',
            field=models.ForeignKey(related_name='default', blank=True, to='orders.CustomFieldValue', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runhookinputmapping',
            name='hook_input',
            field=models.ForeignKey(to='cbhooks.HookInput', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runhookinputmapping',
            name='options',
            field=models.ManyToManyField(related_name='options', null=True, to='orders.CustomFieldValue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='remotescripthook',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='remotescripthook',
            name='os_families',
            field=models.ManyToManyField(help_text='Which OS Families this script is executable on', to='externalcontent.OSFamily', null=True, verbose_name='OS families', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='remotescripthook',
            name='run_on_server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Server', help_text='The server to actually run this script on. Use if you want the script to run on a server other than the one(s) in the current context (e.g. the one(s) being provisioned).', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orchestrationhook',
            name='custom_fields',
            field=models.ManyToManyField(related_name='orchestration_hooks', null=True, to='infrastructure.CustomField', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orchestrationhook',
            name='environments',
            field=models.ManyToManyField(related_name='hooks', null=True, to='infrastructure.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orchestrationhook',
            name='groups',
            field=models.ManyToManyField(related_name='hooks', null=True, to='accounts.Group', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orchestrationhook',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orchestrationhook',
            name='resource_technologies',
            field=models.ManyToManyField(related_name='hooks', null=True, to='resourcehandlers.ResourceTechnology', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookpointaction',
            name='hook',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookpointaction',
            name='hook_point',
            field=models.ForeignKey(to='cbhooks.HookPoint', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookpointaction',
            name='input_mappings',
            field=models.ManyToManyField(to='cbhooks.RunHookInputMapping'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookmapping',
            name='hook',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookmapping',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='resourcehandlers.ResourceNetwork', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookinput',
            name='hook',
            field=models.ForeignKey(related_name='input_fields', to='cbhooks.OrchestrationHook', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowhook',
            name='orchestration_flow',
            field=models.ForeignKey(blank=True, to='orchestrationengines.OrchestrationFlow', help_text='If not specified, the module file will be executed instead', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailhook',
            name='send_to_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
            preserve_default=True,
        ),
    ]
