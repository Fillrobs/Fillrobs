# Generated by Django 2.2.16 on 2021-02-13 01:12

from django.db import migrations

from common.mixins import get_global_id_chars


class Migration(migrations.Migration):
    def set_global_ids(apps, schema_editor):
        ConnectorConfModel = apps.get_model('connectors', 'ConnectorConf')
        prefix = 'CM'
        for row in ConnectorConfModel.objects.all():
            chars = get_global_id_chars()
            row.global_id = f'{prefix}-{chars}'
            row.save()

    dependencies = [
        ('connectors', '0004_connector_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
