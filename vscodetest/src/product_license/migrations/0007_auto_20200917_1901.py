# Generated by Django 2.2.10 on 2020-09-17 19:01

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0005_auto_20200910_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlicense',
            name='modules',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('NAMING', 'naming'), ('BLUECAT_DNS', 'bluecat dns'), ('BLUECAT_IPAM', 'bluecat ipam'), ('INFOBLOX_DNS', 'infoblox dns'), ('INFOBLOX_IPAM', 'infoblox ipam'), ('MICROSOFT_DNS', 'microsoft dns'), ('MEN_AND_MICE_DNS', 'men and mice dns'), ('MEN_AND_MICE_IPAM', 'men and mice ipam')], max_length=107),
        ),
    ]
