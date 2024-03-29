# Generated by Django 3.2.3 on 2021-07-28 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0071_set_slug_for_service_item'),
        ('cbhooks', '0088_auto_20210621_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='orchestrationhook',
            name='blueprints',
            field=models.ManyToManyField(blank=True, help_text='Blueprints which can use this action. If not set, all blueprints can use this action. This is designed for use with Orchestration Actions.', to='servicecatalog.ServiceBlueprint', verbose_name='Blueprints'),
        ),
    ]
