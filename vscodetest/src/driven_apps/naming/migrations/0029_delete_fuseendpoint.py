# Generated by Django 2.2.12 on 2020-06-29 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0009_auto_20200629_1959'),
        ('naming', '0028_endpoint_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FuseEndpoint',
        ),
    ]