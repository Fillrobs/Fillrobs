# Generated by Django 2.2.12 on 2020-06-19 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0024_auto_20200617_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customname',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingjobparameters',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingpolicy',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
        migrations.AlterField(
            model_name='namingsequence',
            name='workspace',
            field=models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group'),
        ),
    ]
