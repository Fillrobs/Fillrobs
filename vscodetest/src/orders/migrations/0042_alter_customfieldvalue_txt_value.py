# Generated by Django 3.2.5 on 2021-12-09 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_alter_customfieldvalue_url_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldvalue',
            name='txt_value',
            field=models.TextField(blank=1, null=1),
        ),
    ]