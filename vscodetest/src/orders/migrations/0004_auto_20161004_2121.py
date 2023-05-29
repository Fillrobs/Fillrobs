# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20160901_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installserviceitemoptions',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='installserviceorderitem',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='preconfigurationvalueset',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='preconfigurationvalueset',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='provisionserverorderitem',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='provisionserverorderitem',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='servermodorderitem',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='servermodorderitem',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
    ]
