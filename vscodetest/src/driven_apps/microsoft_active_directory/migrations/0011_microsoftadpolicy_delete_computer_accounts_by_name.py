# Generated by Django 2.2.10 on 2020-08-25 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microsoft_active_directory', '0010_auto_20200824_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='microsoftadpolicy',
            name='delete_computer_accounts_by_name',
            field=models.BooleanField(default=True),
        ),
    ]
