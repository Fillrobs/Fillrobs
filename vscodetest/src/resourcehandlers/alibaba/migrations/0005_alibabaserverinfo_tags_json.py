# Generated by Django 3.2.5 on 2021-12-02 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alibaba', '0004_alibabaserverinfo_disk_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='alibabaserverinfo',
            name='tags_json',
            field=models.TextField(default='{}'),
        ),
    ]
