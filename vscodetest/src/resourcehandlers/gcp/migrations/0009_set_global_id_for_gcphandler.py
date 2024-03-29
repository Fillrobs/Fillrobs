# Generated by Django 2.2.16 on 2020-12-09 11:23

from django.db import migrations

from common.mixins import get_global_id_chars


class Migration(migrations.Migration):
    def set_global_ids(apps, schema_editor):
        """
        Set random values with appropriate prefixes for the global_id field on
        all existing model entities. The initial schema migration to add the field to the
        model by way of the GlobalIDForAPIMixin will leave all rows
        with the same 8 random characters (and no prefix yet) because the function
        is only called once to calculate the default value for the entire new column
        (https://stackoverflow.com/a/42497696).
        Therefore, we regenerate the 8 random characters to make them different
        across all rows and then add the prefix, like would be done by
        the custom save method for normal object creation.
        """
        GCPHandler = apps.get_model('gcp', 'GCPHandler')
        prefix = 'GCP'
        for row in GCPHandler.objects.all():
            chars = get_global_id_chars()
            row.global_id = f'{prefix}-{chars}'
            row.save()

    dependencies = [
        ('gcp', '0008_gcphandler_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
