# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-19 14:45
from __future__ import unicode_literals

from django.db import migrations


def get_or_create_all_global_cfvs(apps, schema_editor):
    """
    Create the global parameter defaults as custom field mappings with custom field values for global custom fields.
    Gets the provided CustomFields by name, OSFamily by name, and get_or_creates the CustomFieldValues.

    This migration will allow users to delete Global parameter options without them getting recreated on each upgrade
    (removed from cb_minimal and create_objects)

    :param apps:
    :param schema_editor:
    """

    CustomField = apps.get_model("infrastructure", "CustomField")
    OSFamily = apps.get_model("externalcontent", "OSFamily")
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')
    CustomFieldMapping = apps.get_model('behavior_mapping', 'CustomFieldMapping')

    def set_global_default(cf, cfv, os_family_obj, overwrite):
        """
        Copied from CustomField method set_global_default

        Set the global default for this CustomField. If there is already

        value - either a CustomFieldValue object, or a value for one.
        os_family_restriction - the name of an OS family the global mapping should apply to, or
                                the actual os_family object
        overwrite - boolean. When set to False, if a default is already set, this method will do
        nothing.
        """
        cfms = CustomFieldMapping.global_mappings.filter(custom_field=cf, os_family=os_family_obj)
        if not cfms:
            cfm = CustomFieldMapping.objects.create(custom_field=cf, os_family=os_family_obj)
        else:
            cfm = cfms.first()

        if cfm.default and not overwrite:
            # there's already a value set, and we've been asked not to overwrite it, so just return
            return

        cfm.default = cfv

        if os_family_restriction is not None:
            if not isinstance(os_family_restriction, OSFamily):
                os_family = OSFamily.objects.get(name=os_family_restriction)
            else:
                os_family = os_family_restriction
            cfm.os_family = os_family
        else:
            cfm.os_family = None
        cfm.save()

    def create_custom_field(name, label, type, required=False,
                            show_on_servers=False,
                            available_all_servers=False, show_as_attribute=False,
                            description=None):
        """
        THIS IS A TWEAKED COPY OF THE FUNCTION IN C2_WRAPPER AT THE TIME OF THIS MIGRATION
        """

        # Pass type as a default in case a customer has changed the CF from type STR to TXT, or INT to
        # DEC, CB should be okay with that and the upgrader should not fail out.
        custom_field, created = CustomField.objects.get_or_create(
            name=name,
            namespace=None,
            defaults={"type": type},
        )

        if created:
            custom_field.label = label
            custom_field.required = required
            custom_field.show_on_servers = show_on_servers
            custom_field.available_all_servers = available_all_servers
            custom_field.show_as_attribute = show_as_attribute
        # Description can change on existing CF
        custom_field.description = description
        custom_field.save()

        return custom_field

    def create_os_families(family_list, skip=[]):
        # THIS IS A TWEAKED COPY OF THE FUNCTION IN CREATE_OBJECTS AT THE TIME OF THIS MIGRATION
        # Skips the icons part because those aren't needed just to set up the relationship to
        # the global default, will get set with create_objects runs later, and would be complicated
        family_dict = {}
        for info in family_list:
            name = info['name']
            parent = info.get('parent')

            family, _ = OSFamily.objects.get_or_create(name=name)
            family_dict[name] = family
            family.parent = family_dict.get(parent)

            family.save()

    windows_osfam = {
        'name': "Windows",
        'parent': None,
        'inline_icon': "initialize/osfamily-icons/windows-16.png",
        'display_icon': "initialize/osfamily-icons/windows-128.png"
    }

    all_global_cfvs = [
        {
            'field_name': 'new_password',
            'value_field': 'pwd_value',
            'value': 'CloudBolt!',
            'os_family_restriction': 'Windows'
        },
        {
            'field_name': 'time_zone',
            'value_field': 'str_value',
            'value': 'US/Pacific',
            'os_family_restriction': None
        },
        {
            'field_name': 'annotation',
            'value_field': 'txt_value',
            'value': ('Built by {{ server.owner }} '
                      'using CloudBolt {{ portal.site_url|default_if_none:"" }} '
                      'on {{ server.add_date|date:"SHORT_DATE_FORMAT" }} '
                      '[Job ID={{ job.id }}, Order ID={{ order.id }}]'),
            'os_family_restriction': None
        }
    ]

    # Important! These cf field dicts are copied from cb_minimal. If changes are necessary, change in both places.
    annotation_cf = {
        'name': 'annotation',
        'label': 'Annotation',
        'type': 'TXT',
        'required': False,
        'show_on_servers': False,
        'description': (
            "Notes that will be added to AWS or VMware hosts during provisioning. "
            "You may use parameterized templates in this field. "
            "Ex. 'Creator={{ server.owner }} Portal={{ portal.site_url }}'. For more "
            "info, see the docs on hostname templates.")
    }
    new_password_cf = {
        'name': 'new_password',
        'label': 'New Password',
        'type': 'PWD',
        'required': True,
        'description': (
            "This is the password that CB will change the VM to use"
        )
    }
    time_zone_cf = {
        'name': 'time_zone',
        'label': 'Time Zone',
        'type': 'STR',
    }

    all_cfs = [new_password_cf, annotation_cf, time_zone_cf]
    for cf_dict in all_cfs:
        create_custom_field(**cf_dict)

    create_os_families([windows_osfam])

    for cfv_dict in all_global_cfvs:
        field_name = cfv_dict['field_name']
        os_family_restriction = cfv_dict['os_family_restriction']
        cf = CustomField.objects.get(name=field_name)
        os_family = OSFamily.objects.get(name=os_family_restriction) if os_family_restriction else None

        # build a dict for making the CFV with the custom value field name
        cfv_kwargs = {
            'field': cf,
            cfv_dict['value_field']: cfv_dict['value']
        }
        cfv, created = CustomFieldValue.objects.get_or_create(**cfv_kwargs)

        set_global_default(cf=cf, cfv=cfv, os_family_obj=os_family, overwrite=False)


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0017_auto_20171027_1226'),
        ('infrastructure', '0025_customfield_relevant_osfamilies'),
        ('externalcontent', '0005_auto_20170325_1506'),
        ('behavior_mapping', '0009_auto_20180119_1931')  # GlobalMappingsManager must have flag use_in_migrations = True
    ]

    operations = [
        migrations.RunPython(
            get_or_create_all_global_cfvs,  # forwards
            migrations.RunPython.noop,      # backwards
            )
    ]