# Generated by Django 3.2.5 on 2021-10-22 21:24

from django.db import migrations


class Migration(migrations.Migration):
    def add_new_aws_params_to_envs(apps, schema_editor):
        """
        In order to smooth the transition of adding the new Dedicated Host and Dedicated
        Host Group Tech-Specific Parameters to AWS, we want to add them to any existing
        AWS Environment. Otherwise, customers would have to re-import all Tech-specific
        Parameters before being able to use them, which is currently destructive towards
        any customizations they might have made on that Env. There won't be any options
        yet since they're pulled dynamically from AWS, but at least this way people can
        just import the options for these new Parameters specifically since they'll be
        listed on the AWS Parameters tab
        """
        AWSHandler = apps.get_model("aws", "AWSHandler")
        CustomField = apps.get_model("infrastructure", "CustomField")
        # Copied from aws_minimal since this will run first
        cf_name1 = "aws_host"
        cf_dict1 = {
            "label": "Dedicated Host",
            "description": (
                "Launch this instance onto the selected Dedicated Host. Note "
                "that either this or Dedicated Host Group should be selected, and if you "
                "enter a value for both this will take precedence. These options will "
                "also not include any Host that has been added to a Host Resource Group, "
                "as AWS does not allow launching instances on those directly, instead "
                "requiring use of the Group."
            ),
            "type": "STR",
            "required": False,
        }
        cf_name2 = "aws_host_group"
        cf_dict2 = {
            "label": "Dedicated Host Group",
            "description": (
                "Launch this instance into the selected Host Resource Group. Note "
                "that either this or Dedicated Host should be selected, and if you "
                "enter a value for both the specific Dedicated Host will take precedence."
            ),
            "type": "STR",
            "required": False,
        }

        envs = []
        for handler in AWSHandler.objects.all():
            envs.extend(handler.environment_set.all())

        if envs:
            cf1, __ = CustomField.objects.get_or_create(name=cf_name1, defaults=cf_dict1)
            cf2, __ = CustomField.objects.get_or_create(name=cf_name2, defaults=cf_dict2)

            for env in envs:
                env.custom_fields.add(cf1, cf2)

    dependencies = [
        ('aws', '0022_alter_awshandler_ssm_arn'),
    ]

    operations = [
        migrations.RunPython(add_new_aws_params_to_envs, migrations.RunPython.noop),
    ]
