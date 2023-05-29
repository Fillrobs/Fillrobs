# Generated by Django 2.2.10 on 2020-05-06 19:36

from django.db import migrations

def set_workspace_for_existing_content(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    GROUP_TYPE_WORKSPACE = "Workspace"
    DEFAULT_WORKSPACE_NAME = "Default"
    Group = apps.get_model('accounts', 'Group')
    default = Group.objects.filter(
        type__group_type=GROUP_TYPE_WORKSPACE, name=DEFAULT_WORKSPACE_NAME
    ).first()
    model = apps.get_model('naming', 'CustomName')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()

    model = apps.get_model('naming', 'Endpoint')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()

    model = apps.get_model('naming', 'NamingJobParameters')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()

    model = apps.get_model('naming', 'NamingPolicy')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()

    model = apps.get_model('naming', 'NamingSequence')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()

    model = apps.get_model('naming', 'ValidationPolicy')
    for instance in model.objects.all():
        instance.workspace = default
        instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_auto_20200323_1456'),
        ('naming', '0013_auto_20200506_1819'),
    ]

    operations = [
        migrations.RunPython(set_workspace_for_existing_content, migrations.RunPython.noop),
    ]