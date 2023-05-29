# Generated by Django 2.2.10 on 2020-03-23 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, help_text='The time at which this log entry was created')),
                ('severity', models.CharField(choices=[('CRITICAL', 'CRITICAL'), ('ERROR', 'ERROR'), ('WARNING', 'WARNING'), ('NOTICE', 'NOTICE'), ('INFO', 'INFO'), ('DEBUG', 'DEBUG'), ('TRACE', 'TRACE')], help_text='The severity level of this log entry', max_length=10)),
                ('message', models.TextField(blank=True, default='', help_text='The message text for this log entry')),
            ],
            options={
                'verbose_name': 'job log entry',
                'verbose_name_plural': 'job log entries',
                'db_table': 'job_log',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JobMetadata',
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
                'verbose_name': 'job metadata record',
                'verbose_name_plural': 'job metadata records',
                'db_table': 'job_metadata',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='VoltronJob',
        ),
        migrations.AddField(
            model_name='joblog',
            name='job_metadata',
            field=models.ForeignKey(help_text='The Job metadata record that contains this logging entry', on_delete=django.db.models.deletion.CASCADE, to='naming.JobMetadata'),
        ),
    ]
