# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-19 20:48
from __future__ import unicode_literals

from django.db import migrations


def make_cb_admins_super_admins(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    user_profiles = UserProfile.objects.filter(super_admin=False, user__is_superuser=True,
                                               user__is_active=True)
    usernames = list(user_profiles.values_list("user__username", flat=True))
    num_updated = user_profiles.update(super_admin=True)
    print("Found {} users who were CB admins but not super admins and granted them super "
          "admin: {}".format(num_updated, ", ".join(usernames)))


def make_super_admins_cb_admins(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    users = User.objects.filter(is_superuser=False, userprofile__super_admin=True, is_active=True)
    usernames = list(users.values_list("username", flat=True))
    num_updated = users.update(is_superuser=True)
    print("Found {} users who were super admins but not CB admins and granted them CB "
          "admin: {}".format(num_updated, ", ".join(usernames)))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_fix_role_resource_actions_col_name_20180307_1619'),
    ]

    operations = [
        migrations.RunPython(make_cb_admins_super_admins, noop),
        migrations.RunPython(make_super_admins_cb_admins, noop),
    ]