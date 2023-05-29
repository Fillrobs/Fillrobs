# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
        ('utilities', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='VmwareDisk',
            fields=[
                ('disk_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.Disk', on_delete=models.CASCADE)),
                ('vmdk_path', models.CharField(max_length=512)),
                ('node', models.CharField(max_length=24, verbose_name='Virtual device node')),
                ('provisioning_type', models.CharField(max_length=20, choices=[('NONE', 'VMware Template Default'), ('THIN', 'Thin Provision'), ('THICK_LAZY_ZEROED', 'Thick Provision Lazy Zeroed'), ('THICK_EAGER_ZEROED', 'Thick Provision Eager Zeroed')])),
                ('datastore', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=('infrastructure.disk',),
        ),
        migrations.CreateModel(
            name='VmwareNetwork',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('dvSwitch', models.CharField(max_length=100, blank=True)),
                ('adapterType', models.CharField(default='E1000', max_length=6, choices=[('E1000', 'E 1000'), ('VMXN3', 'VMX NET 3')])),
                ('poweron_stage', models.CharField(default='VM_CREATION', max_length=18, choices=[('VM_CREATION', 'On VM Creation'), ('POST_OS_INSTALL', 'Post OS Installation'), ('POST_APP_REMED', 'Post Application Remediation'), ('NONE', 'Manual Poweron')])),
                ('portgroup_key', models.CharField(help_text='The UUID of the portgroup (distributed virtual portgroup objects only)', max_length=100, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'VMware network',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.CreateModel(
            name='VmwareServerInfo',
            fields=[
                ('server', models.OneToOneField(primary_key=True, serialize=False, to='infrastructure.Server', on_delete=models.CASCADE)),
                ('linked_clone', models.BooleanField(default=False)),
                ('cluster', models.CharField(max_length=50)),
                ('snapshots', models.ManyToManyField(to='infrastructure.ServerSnapshot', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VsphereOSBuildAttribute',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('guest_id', models.CharField(max_length=50)),
                ('template_name', models.CharField(max_length=100, null=True, blank=True)),
                ('tools_status', models.CharField(default='Not Installed', help_text='Status of VMware tools on this template as reported by VMware.  Ex. Out of date, Installed, etc.  If set to Not installed, CB will skip network config, changing passwords, and other operations that require vmware tools.', max_length=100)),
                ('total_disk_size', models.DecimalField(help_text='Total size of all disks on this template in GB', null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
            options={
                'verbose_name': 'vSphere OS Build Attribute',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='VsphereResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('clusterName', models.CharField(max_length=100)),
                ('virtual_folder_path', models.CharField(default='CloudBoltVMs/{{ group }}', help_text="\n            Uses the same format as <a\n            href=/static-6dbe029/docs/admin/order-form-customization.html#using-hostname-templates>CloudBolt's\n            hostname templates</a>. Variables available in the context include:<br />\n            * <code>group</code><br />\n            * <code>environment</code><br />\n            * <code>os_build</code><br />\n            * <code>os_family</code><br />\n            * <code>base_os_family</code><br />\n            * <code>service</code> (if running as part of a service installation)<br />\n            * (parameters on the server, e.g. <code>annotations</code>, but not <code>server</code> itself)\n            ", max_length=100)),
                ('clone_tmpl_timeout', models.IntegerField(default=60)),
                ('networks', models.ManyToManyField(related_name='resource_handler', null=True, to='vmware.VmwareNetwork', blank=True)),
                ('nsx_endpoint', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='NSX End-point, used to support advanced networking actions', null=True)),
                ('os_build_attributes', models.ManyToManyField(related_name='resource_handler', null=True, to='vmware.VsphereOSBuildAttribute', blank=True)),
            ],
            options={
                'verbose_name': 'vSphere resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
