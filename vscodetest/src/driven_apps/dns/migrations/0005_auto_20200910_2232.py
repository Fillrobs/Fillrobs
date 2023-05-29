# Generated by Django 2.2.10 on 2020-09-10 22:32

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields.json
import driven_apps.common.mixins
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0052_auto_20200526_0144'),
        ('naming', '0049_auto_20200909_2114'),
        ('dns', '0004_bluecatdnspolicy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dnspolicy',
            name='post_validation_sleep_seconds',
            field=models.TextField(default='5', help_text='(Templatable) Seconds to sleep prior to running post-validate record', validators=[driven_apps.common.validators.IntegerRangeValidator(0, 86400, field_name='postValidationSleepSeconds', template=True)]),
        ),
        migrations.CreateModel(
            name='DnsReservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('records', django_extensions.db.fields.json.JSONField(default=dict, help_text='DNS Records Created.')),
                ('job_metadata', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='naming.JobMetadata')),
                ('policy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dns.DnsPolicy')),
                ('workspace', models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group')),
            ],
            options={
                'verbose_name_plural': 'DNS Reservations',
                'db_table': 'dns_reservations',
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=(models.Model, driven_apps.common.mixins.RoleBasedHalFilteringMixin),
        ),
    ]