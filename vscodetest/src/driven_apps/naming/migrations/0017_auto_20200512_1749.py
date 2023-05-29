# Generated by Django 2.2.12 on 2020-05-12 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0016_auto_20200508_1529'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='endpoint',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='endpoint',
            constraint=models.UniqueConstraint(fields=('type', 'name'), name='endpoint_type_name_unique'),
        ),
    ]