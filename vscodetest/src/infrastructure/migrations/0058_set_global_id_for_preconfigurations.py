# Generated by Django 2.2.16 on 2021-05-06 22:31

from django.db import migrations

from common.mixins import get_global_id_chars


class Migration(migrations.Migration):

    def set_global_ids(apps, schema_editor):
        Model = apps.get_model("infrastructure", "Preconfiguration")
        prefix = "PCF"
        for row in Model.objects.all():
            chars = get_global_id_chars()
            row.global_id = f"{prefix}-{chars}"
            row.save()

    dependencies = [
        ('infrastructure', '0057_preconfiguration_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]