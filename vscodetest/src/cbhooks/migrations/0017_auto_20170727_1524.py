# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0016_orchestrationhook_is_ootb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cloudbolthook',
            name='source_code_url',
            field=models.TextField(blank=True, help_text='\n            Code will be fetched from here before action is run. E.g. URL\n            (without any authentication tokens) to the raw file hosted on your\n            github.com repository or on the <span class="cb-forge-btn"><a class="link no-tooltip-affordance"\n            href="https://github.com/CloudBoltSoftware/cloudbolt-forge"\n            target="_blank"\n            data-toggle="tooltip"\n            data-placement="bottom"\n            title="View and use actions shared by the CloudBolt community (new window)">\n            CloudBolt Forge \n            <i class="glyphicon glyphicon-fire"></i></a></span>\n.  For details \n<a href="/static/docs/advanced/orchestration-actions/actions.html#external-source-code"\n    target="help"\n    class="no-tooltip-affordance"\n    data-toggle="tooltip"\n    data-html="true"\n    title="Learn more in the docs <p>(new window)</p>">\n     see the docs \n    <i class="icon-help"></i>\n</a>\n.\n            ', null=True, verbose_name='URL for source code'),
        ),
        migrations.AlterField(
            model_name='remotescripthook',
            name='source_code_url',
            field=models.TextField(blank=True, help_text='\n            Code will be fetched from here before action is run. E.g. URL\n            (without any authentication tokens) to the raw file hosted on your\n            github.com repository or on the <span class="cb-forge-btn"><a class="link no-tooltip-affordance"\n            href="https://github.com/CloudBoltSoftware/cloudbolt-forge"\n            target="_blank"\n            data-toggle="tooltip"\n            data-placement="bottom"\n            title="View and use actions shared by the CloudBolt community (new window)">\n            CloudBolt Forge \n            <i class="glyphicon glyphicon-fire"></i></a></span>\n.  For details \n<a href="/static/docs/advanced/orchestration-actions/actions.html#external-source-code"\n    target="help"\n    class="no-tooltip-affordance"\n    data-toggle="tooltip"\n    data-html="true"\n    title="Learn more in the docs <p>(new window)</p>">\n     see the docs \n    <i class="icon-help"></i>\n</a>\n.\n            ', null=True, verbose_name='URL for source code'),
        ),
    ]
