# Generated by Django 2.2.12 on 2020-06-19 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0007_auto_20200602_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
