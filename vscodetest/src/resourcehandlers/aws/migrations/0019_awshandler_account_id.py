# Generated by Django 2.2.10 on 2021-01-02 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0018_remove_awshandler_enable_ssm'),
    ]

    operations = [
        migrations.AddField(
            model_name='awshandler',
            name='account_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
