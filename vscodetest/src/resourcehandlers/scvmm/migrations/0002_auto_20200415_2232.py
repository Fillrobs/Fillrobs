# Generated by Django 2.2.10 on 2020-04-15 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scvmm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scvmmhandler',
            name='connection_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utilities.ConnectionInfo'),
        ),
    ]