# Generated by Django 2.2.16 on 2021-04-26 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0080_auto_20210414_1450'),
        ('fuse_servicenow', '0015_servicenowconnectordeployment'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenowconnectorcatalogitem',
            name='job_metadata',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='naming.JobMetadata'),
        ),
    ]
