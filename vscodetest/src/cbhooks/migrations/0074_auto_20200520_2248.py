# Generated by Django 2.2.12 on 2020-05-20 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('itsm', '0001_initial'),
        ('cbhooks', '0073_itsmhook'),
    ]

    operations = [
        migrations.AddField(
            model_name='itsmhook',
            name='itsm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hooks', to='itsm.ITSM'),
        ),
        migrations.AddField(
            model_name='itsmhook',
            name='itsm_technology',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hooks', to='itsm.ITSMTechnology'),
        ),
        migrations.AlterUniqueTogether(
            name='itsmhook',
            unique_together={('itsm_technology', 'itsm')},
        ),
    ]