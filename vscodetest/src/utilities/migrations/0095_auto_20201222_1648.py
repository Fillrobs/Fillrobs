# Generated by Django 2.2.16 on 2020-12-22 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0094_set_global_id_for_ldaputilities'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rootcertificate',
            options={'ordering': ['-id']},
        ),
    ]
