# Generated by Django 2.2.10 on 2020-03-26 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0007_auto_20200325_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='namingjobparameters',
            name='job_metadata',
            field=models.ForeignKey(help_text='Naming job metadata for tracking job progress and logging', null=True, on_delete=django.db.models.deletion.SET_NULL, to='naming.JobMetadata'),
        ),
    ]
