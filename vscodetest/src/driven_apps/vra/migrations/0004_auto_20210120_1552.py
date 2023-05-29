# Generated by Django 2.2.16 on 2021-01-20 15:52

import common.fields
from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('vra', '0003_remove_vrapolicy_user_mapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vrapolicy',
            name='cloud_template_name',
            field=common.fields.TemplatableField(help_text='(Templatable) The Cloud Template Name for this vRealize Automation Policy (A.K.A) Blueprint Name', max_length=65536, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='cloudTemplateName'), driven_apps.common.validators.RegexValidator(field_name='cloudTemplateName', message='Must be alphanumeric characters, underscores, and/or dashes.', regex='^[0-9A-Za-z_.-]*$', template=True)]),
        ),
        migrations.AlterField(
            model_name='vrapolicy',
            name='cloud_template_version_number',
            field=common.fields.TemplatableField(help_text='(Templatable) The Cloud Template Version Number for this vRealize Automation Policy', max_length=65536, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='cloudTemplateVersionNumber'), driven_apps.common.validators.RegexValidator(field_name='cloudTemplateVersionNumber', message='Must be alphanumeric characters, underscores, dashes, dots, and/or asterisks.', regex='^[0-9A-Za-z_*.-]*$', template=True)]),
        ),
        migrations.AlterField(
            model_name='vrapolicy',
            name='name',
            field=models.CharField(help_text='The user-specified name of this vRealize Automation policy.', max_length=255, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='name'), driven_apps.common.validators.MinLengthValidator(constraint=3, field_name='name', required=True), driven_apps.common.validators.RegexValidator(field_name='name', message='Must be alphanumeric characters and/or underscores.', regex='^[0-9A-Za-z_]*$', template=False)]),
        ),
    ]