# Generated by Django 2.2.16 on 2021-02-02 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0016_set_global_id_and_license_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlicense',
            name='license_text',
            field=models.TextField(),
        ),
    ]
