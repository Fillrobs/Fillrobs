# Generated by Django 2.2.12 on 2020-06-29 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0047_auto_20200429_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='azurearmavailableimage',
            name='os_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='azurearmimage',
            name='os_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]