# Generated by Django 2.2.12 on 2020-09-04 14:45

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0045_merge_20200901_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infobloxendpoint',
            name='a_record_template',
            field=models.TextField(default='{"name":"{{request.hostname}}","ipv4addr":"{{request.ipaddress}}","view":"{{endpoint.dnsView}}","comment":"Created by OneFuse"}', help_text='(Templatable) A Record Template', validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='aRecordTemplate', template=True)]),
        ),
        migrations.AlterField(
            model_name='infobloxendpoint',
            name='host_record_template',
            field=models.TextField(default='{"name":"{{request.hostname}}","view":"{{endpoint.dnsView}}","comment":"Created by OneFuse","ipv4addrs":[{"ipv4addr":"{{ request.ipaddress }}"}]}', help_text='(Templatable) Host Record Template', validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='hostRecordTemplate', template=True)]),
        ),
        migrations.AlterField(
            model_name='infobloxendpoint',
            name='ptr_record_template',
            field=models.TextField(default='{"name":"{{request.hostname}}","ptrdname":"{{request.hostname}}","ipv4addr":"{{request.ipaddress}}","view":"{{endpoint.dnsView}}","comment":"Created by OneFuse"}', help_text='(Templatable) Ptr Record Template', validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='ptrRecordTemplate', template=True)]),
        ),
    ]
