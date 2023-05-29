# Generated by Django 2.2.16 on 2020-12-11 21:18

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataprotection', '0003_auto_20200522_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataprotection',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
    ]
