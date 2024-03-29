# Generated by Django 2.2.16 on 2021-03-01 15:50

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0067_increase_service_item_name_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceitem',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
    ]
