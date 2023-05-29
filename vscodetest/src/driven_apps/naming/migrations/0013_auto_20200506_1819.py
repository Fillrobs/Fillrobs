# Generated by Django 2.2.10 on 2020-05-06 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_auto_20200323_1456'),
        ('naming', '0012_auto_20200428_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='customname',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AddField(
            model_name='endpoint',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AddField(
            model_name='namingjobparameters',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AddField(
            model_name='namingpolicy',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AddField(
            model_name='namingsequence',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AddField(
            model_name='validationpolicy',
            name='workspace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
