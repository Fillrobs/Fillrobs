# Generated by Django 2.2.16 on 2021-01-14 17:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infoblox', '0002_rename_existing_infoblox_modules'),
    ]

    operations = [
        migrations.AddField(
            model_name='infobloxipam',
            name='networks_max_results',
            field=models.IntegerField(blank=True, help_text='Used to override the number of results that are accepted when importing networks from Infoblox, for cases where the default value is insufficient and causes an error because there are more networks than that.', null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Maximum # of Network Results'),
        ),
    ]