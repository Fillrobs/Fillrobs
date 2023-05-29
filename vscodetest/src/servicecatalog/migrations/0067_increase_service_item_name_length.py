# Generated by Django 2.2.16 on 2021-02-22 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0066_merge_20210202_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceitem',
            name='name',
            field=models.CharField(blank=True, help_text='Optional name to identify this blueprint item to end users.', max_length=255, null=True, verbose_name='Name'),
        ),
    ]
