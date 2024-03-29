# Generated by Django 2.2.12 on 2020-07-07 20:50

from django.db import migrations


def change_azure_image_version(apps, schema_editor):
    """
    For any existing shared AzureARMImage with a version other than 'lastest',
    set the current version value to os_type, and then set the version to 'latest'.
    """
    AzureARMImage = apps.get_model('azure_arm', 'AzureARMImage')
    for image in AzureARMImage.objects.filter(publisher="shared"):
        if image.version != "latest":
            image.os_type = image.version
            image.version = "latest"
            image.save()


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0049_auto_20200630_0014'),
    ]

    operations = [
        migrations.RunPython(change_azure_image_version, migrations.RunPython.noop)
    ]
