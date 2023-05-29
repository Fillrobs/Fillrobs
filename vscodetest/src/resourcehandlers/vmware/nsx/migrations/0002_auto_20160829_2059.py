# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('vmware', '0001_initial'),
        ('nsx', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nsxscope',
            name='vcenter',
            field=models.ForeignKey(editable=False, to='vmware.VsphereResourceHandler', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nsxscope',
            name='vmware_clusters',
            field=models.ManyToManyField(to='orders.CustomFieldValue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nsxedgeconfiguration',
            name='provider_network',
            field=models.ForeignKey(to='vmware.VmwareNetwork', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nsxedgeconfiguration',
            name='vcenter',
            field=models.ForeignKey(to='vmware.VsphereResourceHandler', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nsxedge',
            name='provider_network',
            field=models.ForeignKey(to='vmware.VmwareNetwork', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nsxedge',
            name='vcenter',
            field=models.ForeignKey(editable=False, to='vmware.VsphereResourceHandler', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
