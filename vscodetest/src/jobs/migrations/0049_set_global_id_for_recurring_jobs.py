# Generated by Django 2.2.16 on 2020-12-18 21:19

from django.db import migrations

from common.mixins import get_global_id_chars


class Migration(migrations.Migration):

    def set_global_ids(apps, schema_editor):
        RecurringJob = apps.get_model("jobs", "RecurringJob")
        prefix = "RJB"
        for row in RecurringJob.objects.all():
            chars = get_global_id_chars()
            row.global_id = f"{prefix}-{chars}"
            row.save()

    dependencies = [
        ('jobs', '0048_recurring_job_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
