# Generated by Django 2.2.10 on 2020-03-12 18:14

import django.core.validators
from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('property_sets', '0003_auto_20200311_1447_squashed_0004_auto_20200311_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyset',
            name='name',
            field=models.CharField(max_length=255, unique=True, validators=[driven_apps.common.validators.not_blank, driven_apps.common.validators.MinLengthValidator(3, True), django.core.validators.RegexValidator('^[0-9A-Za-z_-]*$', 'Must be alphanumeric characters and dashes and/or underscores')]),
        ),
    ]
