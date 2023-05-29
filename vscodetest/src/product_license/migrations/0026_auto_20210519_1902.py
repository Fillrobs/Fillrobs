
from django.db import migrations

def change_license_modules_field(apps, schema_editor):
    ProductLicense = apps.get_model("product_license", "ProductLicense")
    for license in ProductLicense.objects.all():
        license._modules = list(license.modules)
        license.save()



class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0025_productlicense__modules'),
    ]

    operations = [
        migrations.RunPython(change_license_modules_field, migrations.RunPython.noop),
    ]
