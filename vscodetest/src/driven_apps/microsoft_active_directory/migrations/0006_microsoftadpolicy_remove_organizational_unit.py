# Generated by Django 2.2.10 on 2020-08-13 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microsoft_active_directory', '0005_microsoftadpolicy_create_organizational_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='microsoftadpolicy',
            name='remove_organizational_unit',
            field=models.BooleanField(default=False),
        ),
    ]