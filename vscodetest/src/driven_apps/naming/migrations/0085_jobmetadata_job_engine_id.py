# Generated by Django 3.2.3 on 2021-07-02 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0084_alter_servicenowendpoint_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobmetadata',
            name='job_engine_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]