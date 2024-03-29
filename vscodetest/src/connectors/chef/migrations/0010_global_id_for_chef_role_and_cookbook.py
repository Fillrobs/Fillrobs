# Generated by Django 3.2.3 on 2021-07-20 18:47

import common.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chef', '0009_chefconf_delete_node_if_exists'),
    ]

    operations = [
        migrations.AddField(
            model_name='chefcookbook',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
        migrations.AddField(
            model_name='chefrole',
            name='global_id',
            field=models.CharField(default=common.mixins.get_global_id_chars, help_text='Identifier that can be used to access this object through the API across instances.', max_length=16, verbose_name='Global ID'),
        ),
    ]
