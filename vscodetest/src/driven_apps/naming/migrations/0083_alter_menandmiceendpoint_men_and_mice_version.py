# Generated by Django 3.2.3 on 2021-06-25 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0082_alter_namingsequence__naming_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menandmiceendpoint',
            name='men_and_mice_version',
            field=models.CharField(help_text='The Men&Mice Micetro version for this endpoint.', max_length=32, null=True),
        ),
    ]