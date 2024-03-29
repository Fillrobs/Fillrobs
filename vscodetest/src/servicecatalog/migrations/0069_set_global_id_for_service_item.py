# Generated by Django 2.2.16 on 2021-03-01 15:53
from common.mixins import get_global_id_chars
from django.db import migrations


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
        ServiceItem = apps.get_model('servicecatalog', 'ServiceItem')
        prefix = 'BDI'
        for row in ServiceItem.objects.all():
            chars = get_global_id_chars()
            row.global_id = f'{prefix}-{chars}'
            row.save()

    dependencies = [
        ('servicecatalog', '0068_service_item_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
