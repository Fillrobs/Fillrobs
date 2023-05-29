# Generated by Django 2.2.12 on 2020-05-21 14:55

from django.db import migrations, models
import driven_apps.common.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EULA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False, help_text='Indicates whether the EULA been accepted by the user.')),
                ('acceptedOn', models.DateTimeField(help_text='Timestamp of when the EULA was accepted by the user.')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=(models.Model, driven_apps.common.mixins.RoleBasedHalFilteringMixin),
        ),
    ]
