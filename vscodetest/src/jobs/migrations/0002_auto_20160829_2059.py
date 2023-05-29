# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('cbhooks', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('orchestrationengines', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('provisionengines', '0001_initial'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('jobs', '0001_initial'),
        ('utilities', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncvmparameters',
            name='resource_handlers',
            field=models.ManyToManyField(to='resourcehandlers.ResourceHandler', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='syncusersfromldapparameters',
            name='ldap',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.LDAPUtility', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='syncsvrsfrompesparameters',
            name='provision_engines',
            field=models.ManyToManyField(to='provisionengines.ProvisionEngine', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runflowparameters',
            name='flow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='orchestrationengines.OrchestrationFlow', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runflowparameters',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Server', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='progressmessage',
            name='job',
            field=models.ForeignKey(to='jobs.Job', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='networkactionparameters',
            name='manage_nics_job_parameter',
            field=models.ForeignKey(related_name='network_actions', to='jobs.ManageNICsParameters', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='networkactionparameters',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='resourcehandlers.ResourceNetwork', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='managenicsparameters',
            name='server',
            field=models.ForeignKey(to='infrastructure.Server', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobparameters',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='job_parameters',
            field=models.ForeignKey(to='jobs.JobParameters', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='parent_job',
            field=models.ForeignKey(related_name='children_jobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='prereq_job',
            field=models.ForeignKey(related_name='dependent_jobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='rerun_job',
            field=models.OneToOneField(null=1, blank=1, to='jobs.Job', on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installapplicationsparameters',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installapplicationsparameters',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookparameters',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='cbhooks.OrchestrationHook', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookparameters',
            name='hook_point',
            field=models.ForeignKey(to='cbhooks.HookPoint', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hookparameters',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server', null=True),
            preserve_default=True,
        ),
    ]
