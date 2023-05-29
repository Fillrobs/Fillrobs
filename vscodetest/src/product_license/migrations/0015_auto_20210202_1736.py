# Generated by Django 2.2.16 on 2021-02-02 17:36

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0014_auto_20210113_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='productlicense',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
        migrations.AddField(
            model_name='productlicense',
            name='license_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
