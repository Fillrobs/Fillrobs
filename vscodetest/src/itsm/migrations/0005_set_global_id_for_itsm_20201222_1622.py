# Generated by Django 2.2.16 on 2020-12-22 16:22

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
        ITSM = apps.get_model('itsm', 'ITSM')
        prefix = 'ITSM'
        for row in ITSM.objects.all():
            chars = get_global_id_chars()
            row.global_id = f'{prefix}-{chars}'
            row.save()

    dependencies = [
        ('itsm', '0004_itsm_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
