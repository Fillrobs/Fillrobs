# Generated by Django 2.2.12 on 2020-05-14 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0016_set_app_ids_20190923_1137'),
        ('scvmm', '0002_auto_20200415_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='SCVMMTemplate',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute')),
            ],
            options={
                'verbose_name': 'Template',
                'abstract': False,
            },
            bases=('externalcontent.osbuildattribute',),
        ),
    ]
