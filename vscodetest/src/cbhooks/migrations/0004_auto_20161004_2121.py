# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0003_auto_20160901_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailhook',
            name='send_to_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='orchestrationhook',
            name='custom_fields',
            field=models.ManyToManyField(related_name='orchestration_hooks', to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='orchestrationhook',
            name='environments',
            field=models.ManyToManyField(related_name='hooks', to='infrastructure.Environment', blank=True),
        ),
        migrations.AlterField(
            model_name='orchestrationhook',
            name='groups',
            field=models.ManyToManyField(related_name='hooks', to='accounts.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='orchestrationhook',
            name='resource_technologies',
            field=models.ManyToManyField(related_name='hooks', to='resourcehandlers.ResourceTechnology', blank=True),
        ),
        migrations.AlterField(
            model_name='remotescripthook',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='remotescripthook',
            name='os_families',
            field=models.ManyToManyField(help_text='Which OS Families this script is executable on', to='externalcontent.OSFamily', verbose_name='OS families', blank=True),
        ),
        migrations.AlterField(
            model_name='runhookinputmapping',
            name='options',
            field=models.ManyToManyField(related_name='options', to='orders.CustomFieldValue'),
        ),
    ]
