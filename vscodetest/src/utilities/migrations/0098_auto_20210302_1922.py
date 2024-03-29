# Generated by Django 2.2.16 on 2021-03-02 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0097_merge_20210126_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='help_url',
            field=models.URLField(blank=True, help_text="Overrides the 'Support' link in CB's navigation bar.", null=True, verbose_name='URL for site-specific help'),
        ),
    ]
