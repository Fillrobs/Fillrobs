# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from uuid import uuid4

from django.db import migrations

def randomize_nonces(apps, *args):
    """Set all UserProfile nonces to a random UUID

    This is to fix a problem that set all nonces to the same UUID when the
    nonce field was initially added
    """
    UserProfile = apps.get_model("accounts", "UserProfile")
    for profile in UserProfile.objects.all():
        profile.nonce = uuid4()
        profile.save()

def no_op(*args, **kwargs):
    """Do nothing function so that this migration can be reversed if necessary"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_userprofile_temp_user_email'),
    ]

    operations = [
        migrations.RunPython(randomize_nonces, no_op),
    ]
