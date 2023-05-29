# Generated by Django 2.2.10 on 2020-11-06 16:36

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0011_auto_20200925_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlicense',
            name='modules',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('BLUECAT_DNS', 'bluecat dns'), ('BLUECAT_IPAM', 'bluecat ipam'), ('INFOBLOX_DNS', 'infoblox dns'), ('INFOBLOX_IPAM', 'infoblox ipam'), ('MICROSOFT_ACTIVE_DIRECTORY', 'microsoft active directory'), ('MICROSOFT_DNS', 'microsoft dns'), ('MEN_AND_MICE_DNS', 'men and mice dns'), ('MEN_AND_MICE_IPAM', 'men and mice ipam'), ('NAMING', 'naming'), ('SCRIPTING', 'scripting')], max_length=144),
        ),
    ]
