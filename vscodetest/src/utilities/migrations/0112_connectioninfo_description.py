# Generated by Django 3.2.3 on 2021-07-08 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0111_remove_sshkey_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectioninfo',
            name='description',
            field=models.TextField(blank=True, help_text='The description text for this Connection Info.', null=True),
        ),
    ]
