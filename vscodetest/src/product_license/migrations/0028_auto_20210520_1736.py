# Generated by Django 2.2.16 on 2021-05-20 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0027_auto_20210520_1430'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productlicense',
            old_name='_modules',
            new_name='modules',
        ),
    ]