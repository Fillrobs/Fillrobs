# Generated by Django 2.2.16 on 2021-02-18 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
        ('externalcontent', '0017_auto_20201019_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
        migrations.AddField(
            model_name='osbuild',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
        migrations.AddField(
            model_name='osbuildattribute',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
    ]
