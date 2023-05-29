from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slayer', '0006_slayernetwork_is_public'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE resourcehandlers_resourcetechnology SET name = 'IBM Cloud', slug='ibm_cloud', version='1.0' WHERE name = 'IBM SoftLayer';",
            "UPDATE resourcehandlers_resourcetechnology SET name = 'IBM SoftLayer' WHERE name = 'IBM Cloud';"
        )
    ]
