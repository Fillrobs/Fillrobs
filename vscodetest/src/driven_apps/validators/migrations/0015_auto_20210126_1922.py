# Generated by Django 2.2.16 on 2021-01-26 19:22

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0014_auto_20210120_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='name',
            field=models.CharField(help_text='The user-specified name of this validator.', max_length=255, unique=True, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='name'), driven_apps.common.validators.NotBlankValidator(field_name='name', required=True), driven_apps.common.validators.MinLengthValidator(constraint=3, field_name='name', required=True), driven_apps.common.validators.RegexValidator(blank=False, field_name='name', message='Must be alphanumeric characters and/or underscores.', regex='^[0-9A-Za-z_]*$', template=False)]),
        ),
    ]