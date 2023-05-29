# Generated by Django 2.2.10 on 2020-05-06 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0014_auto_20200506_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customname',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingjobparameters',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingpolicy',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingsequence',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='validationpolicy',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
