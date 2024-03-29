# Generated by Django 2.2.16 on 2021-03-31 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0015_set_global_id_for_portalconfig'),
        ('tenants', '0002_auto_20210308_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='portal',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portals.PortalConfig'),
        ),
    ]
