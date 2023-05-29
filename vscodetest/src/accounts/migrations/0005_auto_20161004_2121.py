# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_userprofile_devops_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='environments',
            field=models.ManyToManyField(help_text='An empty list means the env will be available to all environments (unconstrained)', to='infrastructure.Environment', verbose_name='Available Environments', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='inherited_environments',
            field=models.ManyToManyField(related_name='groups_served_by_inheritance', verbose_name='Inherited Environments', to='infrastructure.Environment', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='preconfiguration_options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='preconfigurations',
            field=models.ManyToManyField(to='infrastructure.Preconfiguration', blank=True),
        ),
    ]
