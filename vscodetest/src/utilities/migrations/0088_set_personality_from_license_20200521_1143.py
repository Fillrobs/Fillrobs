# Generated by Django 2.2.12 on 2020-05-21 11:43
from django.db import migrations


def set_personality_if_known(apps, schema_editor):
    """
    For customers who already have a license applied, set the GlobalPreferences.personality that is used to
    track their type of appliance and will be set with a license is applied from now on.
    """
    try:
        # It's ok to skip this migration if the CloudBoltLicense license class is
        # missing because the personality will be set later in product_license
        # migration 0029_move_license_to_db.py
        from product_license.cb_license import CloudBoltLicense
    except Exception:
        return

    the_license = CloudBoltLicense()

    GlobalPreferences = apps.get_model('utilities', 'GlobalPreferences')
    # Can't use usual GlobalPreferences.get() shortcut in a migration
    gp = GlobalPreferences.objects.first()
    # Leave the personality unset if they don't have a valid license
    # Don't change the personality if it's already set, or try to do anything with
    # GlobalPreferences if there isn't an object there yet (fresh install)
    if the_license.is_valid and gp and gp.personality is None:
        if the_license.license_is_for_fuse():
            gp.personality = "Fuse"
        else:
            gp.personality = "CMP"
        gp.save()


def set_personality_to_none(apps, schema_editor):
    """
    To reverse the data migration, just set the personality attribute back to None
    """
    GlobalPreferences = apps.get_model('utilities', 'GlobalPreferences')
    gp = GlobalPreferences.objects.first()
    if gp:
        gp.personality = None
        gp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0087_globalpreferences_personality'),
    ]

    operations = [
        migrations.RunPython(set_personality_if_known, set_personality_to_none),
    ]
