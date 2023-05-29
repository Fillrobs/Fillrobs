# Generated by Django 3.2.5 on 2021-11-04 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0005_set_global_id_for_tenant_models'),
        ('accounts', '0062_new_delegate_server_owner_role_20211013_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_profiles', to='tenants.tenant'),
        ),
    ]
