# Generated by Django 3.2.5 on 2021-11-16 20:10

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0090_auto_20210720_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='infobloxendpoint',
            name='cname_record_template',
            field=models.TextField(default='{"name":"{{request.name}}","canonical":"{{request.value}}","view":"{{endpoint.dnsView}}","comment":"Created by OneFuse"}', help_text='(Templatable) CName Record Template', validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='cNameRecordTemplate', template=True)]),
        ),
    ]