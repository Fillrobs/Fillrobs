from django.db import migrations

from common.mixins import get_global_id_chars


def set_global_ids(apps, schema_editor):
    """
    Set random values with appropriate prefixes for the global_id field on
    all existing LDAPUtility entities. The initial schema migration to add the field to the
    LDAPUtility model by way of the GlobalIDForAPIMixin will leave all utilities
    with the same 8 random characters (and no prefix yet) because the function
    is only called once to calculate the default value for the entire new column
    (https://stackoverflow.com/a/42497696).
    Therefore, we regenerate the 8 random characters to make them different
    across the utilities and then add the prefix, like would be done by
    the custom save method for normal object creation.
    """
    LDAPUtility = apps.get_model('utilities', 'LDAPUtility')
    prefix = 'IDD-'
    for idd in LDAPUtility.objects.all():
        chars = get_global_id_chars()
        idd.global_id = '{}{}'.format(prefix, chars)
        idd.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0093_ldaputility_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids,
                             migrations.RunPython.noop),
    ]
