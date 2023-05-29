# Generated by Django 2.2.16 on 2020-12-10 14:46

import common.fields
import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extensions', '0003_auto_20190814_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='uiextension',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='uiextension',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
        migrations.AddField(
            model_name='uiextension',
            name='list_image',
            field=common.fields.PreviewImageField(blank=True, default='', help_text='Any size. All standard image formats work, though PNGs with alpha transparency look best.', null=True, upload_to='uix/', verbose_name='List Image'),
        ),
    ]
