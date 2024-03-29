# Generated by Django 2.2.12 on 2020-06-02 20:54

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('property_sets', '0009_auto_20200514_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyset',
            name='name',
            field=models.CharField(max_length=255, unique=True, validators=[driven_apps.common.validators.NotBlankValidator(field_name='name', required=True), driven_apps.common.validators.MinLengthValidator(constraint=3, field_name='name', required=True), driven_apps.common.validators.RegexValidator(field_name='name', message='Must be alphanumeric characters and/or underscores.', regex='^[0-9A-Za-z_]*$')]),
        ),
        migrations.AlterField(
            model_name='propertyset',
            name='type',
            field=models.CharField(choices=[('static', 'static'), ('dynamic', 'dynamic')], max_length=255, validators=[driven_apps.common.validators.OneOfValidator(allowed_values=['dynamic', 'static'], field_name='type')]),
        ),
    ]
