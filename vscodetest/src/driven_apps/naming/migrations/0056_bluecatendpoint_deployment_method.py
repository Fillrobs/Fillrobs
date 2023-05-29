# Generated by Django 2.2.10 on 2020-09-25 19:12

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0055_auto_20200924_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluecatendpoint',
            name='deployment_method',
            field=models.CharField(default='SELECTIVE_DEPLOY', help_text='DNS deployment method.', max_length=64, validators=[driven_apps.common.validators.OneOfValidator(allowed_values=['SELECTIVE_DEPLOY'], field_name='deploymentMethod')]),
        ),
    ]