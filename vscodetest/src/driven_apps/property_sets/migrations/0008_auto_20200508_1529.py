# Generated by Django 2.2.12 on 2020-05-08 15:29

import django.core.validators
from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('property_sets', '0007_auto_20200506_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyset',
            name='name',
            field=models.CharField(max_length=255, unique=True, validators=[driven_apps.common.validators.not_blank, driven_apps.common.validators.MinLengthValidator(3, True), django.core.validators.RegexValidator('^[0-9A-Za-z_]*$', 'Must be alphanumeric characters and/or underscores.')]),
        ),
    ]
