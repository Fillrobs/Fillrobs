# Generated by Django 2.2.16 on 2021-02-22 10:13

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0021_merge_20210222_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlicense',
            name='modules',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('ANSIBLE_TOWER', 'ansible tower'), ('BLUECAT_DNS', 'bluecat dns'), ('BLUECAT_IPAM', 'bluecat ipam'), ('INFOBLOX_DNS', 'infoblox dns'), ('INFOBLOX_IPAM', 'infoblox ipam'), ('MEN_AND_MICE_DNS', 'men and mice dns'), ('MEN_AND_MICE_IPAM', 'men and mice ipam'), ('MICROSOFT_ACTIVE_DIRECTORY', 'microsoft active directory'), ('MICROSOFT_DNS', 'microsoft dns'), ('NAMING', 'naming'), ('SCRIPTING', 'scripting'), ('SERVICENOWCMDB', 'servicenow cmdb'), ('VRA', 'vrealize automation'), ('CONNECTOR', 'connector'), ('SERVICE_CATALOG', 'service catalog'), ('SDN', 'software defined network'), ('ORCHESTRATION', 'orchestration'), ('PROVISIONING_ENGINE', 'provisioning engine'), ('REPORT', 'report'), ('MULTITENANCY', 'multitenancy')], max_length=261),
        ),
    ]