# Generated by Django 2.2.16 on 2021-05-20 13:39

from django.db import migrations


def associate_cfvs(apps, schema_editor):
    """
    For every current SSHKey object, populate its key_reference FK with the
    appropriate CustomFieldValue. We expect them to already exist, but use
    get_or_create so we can create just in case one doesn't.
    This is not only necessary for proper SSH Key functionality going
    forward, but also allows us to add a non-nullable ForeignKey when placed
    between 0106 and 0108
    """
    SSHKey = apps.get_model('utilities', 'SSHKey')
    CustomField = apps.get_model('infrastructure', 'CustomField')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')

    for key in SSHKey.objects.all():
        name_cf, __ = CustomField.objects.get_or_create(name="key_name")
        key_name_cfv, __ = CustomFieldValue.objects.get_or_create(
            field=name_cf, str_value=key.name
        )
        key.key_reference = key_name_cfv
        key.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0106_sshkey_key_reference'),
        ('infrastructure', '0058_set_global_id_for_preconfigurations'),
        ('orders', '0039_orderitem_global_id'),
    ]

    operations = [
        migrations.RunPython(associate_cfvs, migrations.RunPython.noop),
    ]
