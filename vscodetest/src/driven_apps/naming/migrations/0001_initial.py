# Generated by Django 2.2.10 on 2020-03-05 19:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import driven_apps.common.validators
import driven_apps.policies.classes


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0035_auto_20200213_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('dns_suffix', models.CharField(max_length=253)),
            ],
            options={
                'verbose_name_plural': 'Custom Names',
                'db_table': 'custom_name',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NamingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=1024)),
            ],
            options={
                'verbose_name_plural': 'Naming Data',
                'db_table': 'naming_data',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NamingSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_value', models.CharField(blank=True, max_length=1024, null=True)),
                ('initial_value', models.CharField(max_length=1024)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('pattern_format', models.CharField(blank=True, max_length=1024, null=True)),
                ('last_value', models.CharField(blank=True, max_length=1024, null=True)),
                ('length', models.IntegerField(blank=True, null=True, validators=[
                    driven_apps.common.validators.MinValueValidator(1, False)])),
                ('name', models.CharField(max_length=255, unique=True, validators=[driven_apps.common.validators.not_blank, driven_apps.common.validators.MinLengthValidator(3, True), django.core.validators.RegexValidator('^[0-9A-Za-z_-]*$', 'Must match ^[0-9A-Za-z_-]*$')])),
                ('pad', models.CharField(blank=True, max_length=1024, null=True, validators=[
                    driven_apps.common.validators.MaxLengthValidator(1, False)])),
                ('reuse', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('BASE8', 'Octal'), ('BASE10', 'Decimal'), ('BASE16', 'Hexadecimal'), ('PATTERN', 'Pattern')], max_length=50, validators=[
                    driven_apps.common.validators.OneOfValidator(('BASE8', 'BASE10', 'BASE16', 'PATTERN'))])),
                ('unique_key', models.CharField(blank=True, max_length=1024, null=True)),
                ('_naming_data', models.CharField(default='{}', max_length=1024)),
            ],
            options={
                'verbose_name_plural': 'Naming Sequences',
                'db_table': 'naming_sequence',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ValidationPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Validation Policies',
                'db_table': 'validation_policy',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VoltronJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_type', models.CharField(choices=[('crud', 'crud'), ('module', 'module')], max_length=1024)),
                ('job_state', models.CharField(choices=[('Initialized', 'Initialized'), ('In_Progress', 'In Progress'), ('Successful', 'Successful'), ('Canceled', 'Canceled'), ('Failed', 'Failed')], max_length=1024)),
                ('job_id', models.CharField(max_length=1024)),
                ('job_tracking_id', models.CharField(max_length=1024)),
                ('source', models.CharField(max_length=1024)),
                ('requester', models.CharField(blank=True, max_length=1024, null=True)),
                ('module', models.CharField(blank=True, max_length=1024, null=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('policy_name', models.CharField(blank=True, max_length=1024, null=True)),
                ('_request_info', models.TextField(blank=True, default='{}', null=True)),
                ('_response_info', models.TextField(blank=True, default='{}')),
            ],
            options={
                'verbose_name_plural': 'Voltron Jobs',
                'db_table': 'voltron_job',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NamingPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.CharField(max_length=1024, validators=[driven_apps.common.validators.not_blank])),
                ('name', models.CharField(max_length=254, unique=True, validators=[driven_apps.common.validators.not_blank, driven_apps.common.validators.MinLengthValidator(3, True), django.core.validators.RegexValidator('^[0-9A-Za-z_-]*$', 'Must be alphanumeric characters and dashes and/or underscores')])),
                ('description', models.CharField(blank=True, default='', max_length=1024)),
                ('dns_suffix', models.CharField(blank=True, default='', max_length=253, validators=[django.core.validators.RegexValidator('(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\\.)+[a-zA-Z]{2,63}$)', 'Must be valid dns')])),
                ('naming_data', models.ManyToManyField(blank=True, to='naming.NamingData')),
                ('naming_sequences', models.ManyToManyField(blank=True, related_name='naming_sequences', to='naming.NamingSequence')),
                ('validation_policies', models.ManyToManyField(blank=True, to='naming.ValidationPolicy')),
            ],
            options={
                'verbose_name_plural': 'Naming Policies',
                'db_table': 'naming_policy',
                'ordering': ['id'],
                'abstract': False,
            },
            bases=(models.Model, driven_apps.policies.classes.GenericPolicy),
        ),
        migrations.CreateModel(
            name='NamingJobParameters',
            fields=[
                ('jobparameters_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jobs.JobParameters')),
                ('json_payload', models.TextField()),
                ('template_properties', models.TextField(default='{}')),
                ('result', models.TextField(default='{}')),
                ('errors', models.TextField(default='{}')),
                ('policy', models.ForeignKey(help_text='Naming policy to use to generate the name. If left blank, the job will select the appropriate policy based on the payload', null=True, on_delete=django.db.models.deletion.SET_NULL, to='naming.NamingPolicy')),
            ],
            options={
                'verbose_name_plural': 'Naming Job Parameters',
                'db_table': 'namingjobparameters',
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('jobs.jobparameters', models.Model),
        ),
    ]
