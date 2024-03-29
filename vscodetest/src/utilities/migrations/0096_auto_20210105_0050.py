# Generated by Django 2.2.16 on 2021-01-05 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0095_auto_20201222_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='restrict_new_environments',
            field=models.BooleanField(default=True, help_text='When new CB environments are created, instead of being available to all groups, restrict them to only the unassigned group (and thus do not show them in the order form until they are exposed to more groups).'),
        ),
    ]
