# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cb_secrets.fields
import common.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReportingEngine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scheme', models.CharField(default='http', help_text='Scheme/protocol used to connect to this reporting engine', max_length=10, choices=[('http', 'http'), ('https', 'https')])),
                ('host', models.CharField(default='localhost', help_text='IP address/hostname used to connect to this reporting engine', max_length=50)),
                ('port', models.IntegerField(default='8080', help_text='Port used to connect to this reporting engine', validators=[common.validators.is_only_digits])),
                ('reports_path', models.CharField(default='/reports/cloudbolt', help_text='Path to where CloudBolt reports are stored in this reporting engine', max_length=200)),
                ('default_format', models.CharField(default='pdf', help_text='Default report format to use for this reporting engine', max_length=10, choices=[('pdf', 'pdf'), ('csv', 'csv'), ('rtf', 'rtf'), ('xls', 'xls'), ('xml', 'xml')])),
                ('serviceaccount', models.CharField(default='jasperadmin', help_text='Authorized user to list and run reports in reports_pathfor this reporting engine', max_length=50)),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(default='jasperadmin', help_text='Password for authorized user to list and run reports in reports_path for this reporting engine')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
