# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import costs.models
import servicecatalog.models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('containerorchestrators', '0001_initial'),
        ('networks', '0002_auto_20160829_2059'),
        ('cbhooks', '0001_initial'),
        ('orders', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceBlueprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(null=True, blank=True)),
                ('list_image', models.ImageField(default='', upload_to='services/', blank=True, help_text='Any size. All standard image formats work, though PNGs with alpha transparency look best.', null=True)),
                ('status', models.CharField(default='ACTIVE', max_length=10, choices=[('ACTIVE', 'Active'), ('HISTORICAL', 'Historical')])),
                ('sequence', models.IntegerField(default=0, help_text='Sequence specifies the order (followed by blueprint name) that blueprints appear in the service catalog. Lower-number sequence numbers will show up first. (default=0)')),
                ('service_name_template', models.CharField(help_text='Specify a template for generating deployed service names', max_length=255, null=True, blank=True)),
                ('custom_field_options', models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True)),
                ('custom_fields_for_service', models.ManyToManyField(related_name='serviceblueprint_set_for_service', null=True, to='infrastructure.CustomField', blank=True)),
                ('custom_fields_for_sis', models.ManyToManyField(related_name='serviceblueprint_set_for_sis', null=True, to='infrastructure.CustomField', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceBlueprintGroupPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(max_length=8, choices=[('MANAGE', 'Manage'), ('DEPLOY', 'Deploy')])),
                ('blueprint', models.ForeignKey(to='servicecatalog.ServiceBlueprint', on_delete=models.CASCADE)),
                ('group', models.ForeignKey(to='accounts.Group', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Service blueprint group permission',
                'verbose_name_plural': 'Service blueprint group permissions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Optional name to identify this service item to end users.', max_length=75, null=True, blank=True)),
                ('description', models.TextField(help_text='Optional detailed description about this service item for end users.', null=True, blank=True)),
                ('deploy_seq', models.IntegerField(help_text='Order in which service items of a service will be deployed.', null=True, blank=True)),
                ('execute_in_parallel', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['deploy_seq', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RunWebHookServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.CreateModel(
            name='RunRemoteScriptHookServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.CreateModel(
            name='RunFlowHookServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.CreateModel(
            name='RunEmailHookServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.CreateModel(
            name='RunCloudBoltHookServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.CreateModel(
            name='ProvisionServerServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('hostname_template', models.CharField(default='', max_length=255)),
                ('all_environments_enabled', models.BooleanField(default=False)),
                ('applications', models.ManyToManyField(to='externalcontent.Application', null=True, blank=True)),
                ('os_build', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', servicecatalog.models.ServiceItemWithEnvParametersMixin),
        ),
        migrations.CreateModel(
            name='NetworkServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('ipv4_block', models.CharField(help_text='IPv4 range in CIDR notation', max_length=20, verbose_name='IPv4 Block', validators=[django.core.validators.RegexValidator(regex='^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\/([0-9]|[1-2][0-9]|3[0-2])$')])),
                ('servers', models.ManyToManyField(help_text='Servers to put on this new network when they are provisioned.', related_name='networks', null=True, to='servicecatalog.ProvisionServerServiceItem', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(costs.models.NoRateImpactMixin, 'servicecatalog.serviceitem'),
        ),
        migrations.CreateModel(
            name='LoadBalancerServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('name_template', models.CharField(default='', max_length=255)),
                ('source_port', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('destination_port', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('_extra_args', models.TextField(default='{}', help_text='JSON representation of the dictionary of name/value pairs to be passed to create load balancer action.')),
                ('lb_tech', models.ForeignKey(verbose_name='Load Balancer Technology', blank=True, to='networks.LoadBalancerTechnology', null=True, on_delete=models.SET_NULL)),
                ('servers', models.ManyToManyField(help_text='Servers to load balance. If left blank, will load balance all servers built up to this point in the service.', related_name='load_balancers', null=True, to='servicecatalog.ProvisionServerServiceItem', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(costs.models.NoRateImpactMixin, 'servicecatalog.serviceitem'),
        ),
        migrations.CreateModel(
            name='InstallPodServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('images', models.TextField(help_text='Comma-separated list of images of containers to install as part of this pod')),
                ('container_orchestrator', models.ForeignKey(to='containerorchestrators.ContainerOrchestrator', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem',),
        ),
        migrations.CreateModel(
            name='TearDownServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('continue_on_failure', models.BooleanField(default=False)),
                ('run_on_scale_up', models.BooleanField(default=True)),
                ('hook', models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT)),
                ('input_mappings', models.ManyToManyField(to='cbhooks.RunHookInputMapping')),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem', models.Model, costs.models.NoRateImpactMixin),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='blueprint',
            field=models.ForeignKey(to='servicecatalog.ServiceBlueprint', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='enabled_environments',
            field=models.ManyToManyField(related_name='enabled_service_items', null=True, to='infrastructure.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serviceblueprint',
            name='groups',
            field=models.ManyToManyField(related_name='editable_services', through='servicecatalog.ServiceBlueprintGroupPermissions', to='accounts.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='runremotescripthookserviceitem',
            name='targets',
            field=models.ManyToManyField(help_text='This script will run on all servers created by the specified service item.If no targets are selected, script will be run on all servers created by this service (at the time when the script runs)', related_name='script_hooks_to_run', null=True, to='servicecatalog.ProvisionServerServiceItem', blank=True),
            preserve_default=True,
        ),
    ]
