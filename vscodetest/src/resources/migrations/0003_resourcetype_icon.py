# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-27 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_move_services_app_objs_to_resources_app_20180201_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcetype',
            name='icon',
            field=models.CharField(blank=True, default='', help_text='Optionally provide a special icon to be displayed for this Resource Type. Must correspond to an available icon name, such as "icon-delete", "glyphicon glyphicon-time", or "fas fa-heartbeat". For more examples, see <a href="http://fortawesome.github.io/Font-Awesome/icons/">Font Awesome</a> and <a href="http://getbootstrap.com/components/">Glyphicons</a>.', max_length=255),
        ),
    ]