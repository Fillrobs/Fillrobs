# Generated by Django 2.2.10 on 2020-10-19 17:09

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0053_encrypt_security_answers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
    ]
