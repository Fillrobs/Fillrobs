# Generated by Django 2.2.16 on 2021-02-09 03:36

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containerorchestrators', '0009_auto_20191204_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='containerorchestrator',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
    ]
