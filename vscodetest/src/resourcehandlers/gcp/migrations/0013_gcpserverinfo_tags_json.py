# Generated by Django 3.2.3 on 2021-07-21 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcp', '0012_gcpnetwork_set_network_for_sharedvpc'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcpserverinfo',
            name='tags_json',
            field=models.TextField(default='{}'),
        ),
    ]
