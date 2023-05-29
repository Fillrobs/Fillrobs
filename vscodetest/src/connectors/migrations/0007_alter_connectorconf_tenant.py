# Generated by Django 3.2.5 on 2021-11-04 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0005_set_global_id_for_tenant_models'),
        ('connectors', '0006_merge_20210226_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectorconf',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant'),
        ),
    ]