# Generated by Django 2.2.10 on 2020-03-09 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solarwindsipam', '0002_solarwindsipamnetwork'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solarwindsipamnetwork',
            name='subnet_id',
            field=models.CharField(max_length=50),
        ),
    ]
