# Generated by Django 2.2.10 on 2020-05-06 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_auto_20200323_1456'),
        ('validators', '0002_auto_20200428_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='validator',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
