# Generated by Django 2.2.10 on 2020-03-20 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_randomize_nonces'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='configuration_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='workspace_creator',
            field=models.BooleanField(default=False),
        ),
    ]