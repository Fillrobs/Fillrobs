# Generated by Django 2.2.10 on 2020-08-27 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microsoft_active_directory', '0011_microsoftadpolicy_delete_computer_accounts_by_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='microsoftadcomputeraccount',
            name='state',
            field=models.CharField(choices=[('build', 'BUILD'), ('final', 'FINAL')], default=None, max_length=40, null=True),
        ),
    ]
