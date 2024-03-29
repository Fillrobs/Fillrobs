# Generated by Django 2.2.16 on 2020-11-20 19:19

from django.db import migrations


def update_message(message: str, leading: str, trailing: str) -> str:
    """
    Strip the b'...' around message strings that we improperly encoded,
    and remove any errant leading or trailing whitespace.
    """
    return message.lstrip(leading).rstrip(trailing).strip()


def update_history_event_messages(apps, schema_editor):
    """
    Clean up old History `event_messages` that were improperly encoded.
    """
    HistoryModel = apps.get_model('history', 'HistoryModel')

    for leading, trailing in (("b'", "'"), ('b"', '"')):
        history_objects = HistoryModel.objects.filter(
            event_message__startswith=leading, event_message__endswith=trailing
        )

        for history_obj in history_objects:
            history_obj.event_message = update_message(history_obj.event_message, leading, trailing)

        HistoryModel.objects.bulk_update(history_objects, ["event_message"], batch_size=1024)


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0018_actionhistory'),
    ]

    operations = [
        migrations.RunPython(update_history_event_messages, migrations.RunPython.noop),
    ]
