# Generated by Django 2.2.16 on 2021-02-24 23:56

from django.db import migrations

from common.mixins import get_global_id_chars


class Migration(migrations.Migration):

    def set_global_ids(apps, schema_editor):
        PEModel = apps.get_model("provisionengines", "ProvisionEngine")
        prefix = "PE"
        for row in PEModel.objects.all():
            chars = get_global_id_chars()
            row.global_id = f"{prefix}-{chars}"
            row.save()

    dependencies = [
        ("provisionengines", "0003_add_global_id"),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]