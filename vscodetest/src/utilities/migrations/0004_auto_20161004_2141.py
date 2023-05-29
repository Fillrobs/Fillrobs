# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0003_globalpreferences_allow_exceeding_quotas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pkiutility',
            name='new_user_approver',
            field=models.ManyToManyField(related_name='create_as_approver', verbose_name='Auto-create as approver for', to='accounts.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='pkiutility',
            name='new_user_environment_manager',
            field=models.ManyToManyField(related_name='create_as_environment_manager', verbose_name='Auto-create as environment manager for', to='accounts.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='pkiutility',
            name='new_user_group_manager',
            field=models.ManyToManyField(related_name='create_as_group_manager', verbose_name='Auto-create as group manager for', to='accounts.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='pkiutility',
            name='new_user_requestor',
            field=models.ManyToManyField(related_name='create_as_requestor', verbose_name='Auto-create as requestor for', to='accounts.Group', blank=True),
        ),
    ]
