# Generated by Django 2.2.16 on 2021-03-08 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0059_set_global_id_for_userprofile'),
        ('infrastructure', '0054_auto_20210218_1007'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='default_environment',
            field=models.ForeignKey(help_text='The Environment that Servers in this Tenant will be added to on discovery by default, if the correct Environment for the Resource Handler is not clear', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='default_for_tenant', to='infrastructure.Environment', verbose_name='Default Environment for Discovery'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='default_group',
            field=models.ForeignKey(help_text='The Group that Servers in this Tenant will be added to on discovery', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='default_for_tenant', to='accounts.Group', verbose_name='Default Group for Discovery'),
        ),
    ]
