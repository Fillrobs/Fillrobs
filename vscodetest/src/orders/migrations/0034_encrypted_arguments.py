# Generated by Django 2.2.16 on 2021-03-02 22:43

import cb_secrets.fields
from django.db import migrations


def encrypt_arguments(apps, schema_editor):
    ActionJobOrderItem = apps.get_model("orders", "ActionJobOrderItem")
    for row in ActionJobOrderItem.objects.all():
        row._encrypted_arguments = row._arguments
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0033_customfieldvalue_tenant"),
    ]

    operations = [
        migrations.AddField(
            model_name="actionjoborderitem",
            name="_encrypted_arguments",
            field=cb_secrets.fields.EncryptedTextField(
                blank=True,
                help_text="JSON representation of the dictionary of name/value pairs to be passed to this action.",
                null=True,
            ),
        ),
        migrations.RunPython(encrypt_arguments, migrations.RunPython.noop),
    ]
