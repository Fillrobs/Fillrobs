# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0005_serviceblueprint_any_group_can_deploy'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlueprintServiceItem',
            fields=[
                ('serviceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='servicecatalog.ServiceItem', on_delete=models.CASCADE)),
                ('sub_blueprint', models.ForeignKey(to='servicecatalog.ServiceBlueprint', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('servicecatalog.serviceitem',),
        ),
        migrations.AddField(
            model_name='serviceblueprint',
            name='is_sub_blueprint',
            field=models.BooleanField(default=False, help_text='Specify whether this catalog item should be available for inclusion in other blueprints'),
            preserve_default=True,
        ),
    ]
