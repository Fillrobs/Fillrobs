# Generated by Django 2.2.10 on 2020-04-17 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0002_remove_basessoprovider_allow_unsolicited'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basessoprovider',
            name='_required_attributes',
            field=models.CharField(blank=True, default='email,username,first_name,last_name', help_text='The combination of attributes that this SP will use for verifying a User that is sent from the IdP', max_length=512, verbose_name='Required Attributes'),
        ),
    ]
