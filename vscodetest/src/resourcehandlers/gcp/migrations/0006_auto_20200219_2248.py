# Generated by Django 2.2.10 on 2020-02-19 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcp', '0005_auto_20200127_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcpproject',
            name='service_account_email',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gcpproject',
            name='service_account_key',
            field=models.TextField(blank=True, null=True),
        ),
    ]
