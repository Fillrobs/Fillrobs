# Generated by Django 2.2.10 on 2020-03-24 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0004_auto_20200324_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblog',
            name='job_metadata',
            field=models.ForeignKey(help_text='The Job metadata record that contains this logging entry', on_delete=django.db.models.deletion.CASCADE, to='naming.JobMetadata'),
        ),
    ]