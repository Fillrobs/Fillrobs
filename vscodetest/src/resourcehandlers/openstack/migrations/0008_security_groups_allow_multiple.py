# Generated by Django 2.2.10 on 2020-03-23 13:49

from django.db import migrations

def security_groups_allow_multiple(apps, schema_editor):
	"""
	One-time migration for existing customers to set allow_multiple = True on
        the OpenStack security group parameter, which used to only allow a single value.
	"""
	CustomField = apps.get_model('infrastructure', 'CustomField')
	try:
		cf = CustomField.objects.get(name='sec_groups')
	except CustomField.DoesNotExist:
		# CF doesn't exist and will be created by cb_minimal
		return
	cf.allow_multiple = True
	cf.save()
		
class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0007_remove_openstackhandler_old_os_build_attributes'),
    ]

    operations = [
	migrations.RunPython(
		security_groups_allow_multiple, migrations.RunPython.noop
		)
    ]
