# Generated by Django 2.2.10 on 2020-01-30 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0012_merge_20190315_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='awshandler',
            name='SSM_ARN',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
