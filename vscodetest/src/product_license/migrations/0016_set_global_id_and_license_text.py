from django.db import migrations

from product_license.license_service import LicenseService


class Migration(migrations.Migration):
    def force_replace_license(apps, schema_editor):
        """
        license_text has to come from the original license file, and this should be fine because
        up to this point the appliance supported a single license and left it in the filesystem at
        /var/opt/cloudbolt/license.bin
        """
        try:
            from product_license import cb_license
        except Exception:
            # If cb_license no longer exists we can safely skip the migration.
            # The license will be moved to the database in a later migration.
            return

        ProductLicense = apps.get_model('product_license', 'ProductLicense')
        ProductLicense.objects.all().delete()
        license = cb_license.CloudBoltLicense()
        if license.state in [cb_license.LICENSE_EXPIRED, cb_license.LICENSE_GOOD]:
            _ = LicenseService().add_license(license.ciphertext)

    dependencies = [
        ('product_license', '0015_auto_20210202_1736'),
    ]

    operations = [migrations.RunPython(force_replace_license, migrations.RunPython.noop)]
