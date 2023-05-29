# Generated by Django 2.2.16 on 2021-03-02 21:10

import common.fields
from django.db import migrations
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('vra', '0009_auto_20210302_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vra8policy',
            name='verify_new_deployment_owner',
        ),
        migrations.AlterField(
            model_name='vra8policy',
            name='user_mapping',
            field=common.fields.TemplatableField(blank=True, default='{{ deploymentOwner | required }}', help_text='(Templatable) User mapping', max_length=65536, null=True, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='userMapping', template=True)]),
        ),
    ]