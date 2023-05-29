# Generated by Django 2.2.10 on 2020-09-25 13:22

import common.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0018_resourcehandler_include_vm_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcehandler',
            name='ip',
            field=models.CharField(max_length=254, validators=[common.validators.validate_domain_or_ip], verbose_name='IP address'),
        ),
        migrations.AlterField(
            model_name='resourcehandler',
            name='name',
            field=models.CharField(help_text='Display name. Not used in any programmatic fashion and can be changed safely.', max_length=254, verbose_name='Name'),
        ),
    ]
