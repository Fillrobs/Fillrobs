# Generated by Django 2.2.10 on 2020-05-06 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0004_auto_20200506_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
