# Generated by Django 3.2.3 on 2021-08-12 20:37

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
        AnsiblePlaybook = apps.get_model("ansible", "AnsiblePlaybook")
        prefix = "ACP"
        for row in AnsiblePlaybook.objects.all():
            chars = get_global_id_chars()
            row.global_id = f"{prefix}-{chars}"
            row.save()

    dependencies = [
        ('ansible', '0013_set_global_id_for_ansible_groups'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
