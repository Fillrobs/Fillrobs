
from common.mixins import get_global_id_chars
from django.db import migrations, models


class Migration(migrations.Migration):

    def set_global_ids(apps, schema_editor):
        prefix = "PTL"
        portalConfigModel = apps.get_model('portals', 'PortalConfig')

        for row in portalConfigModel.objects.all():
            chars = get_global_id_chars()
            row.global_id = f'{prefix}-{chars}'
            row.save()

    dependencies = [
        ('portals', '0014_portalconfig_global_id'),
    ]

    operations = [
        migrations.RunPython(set_global_ids, migrations.RunPython.noop),
    ]
