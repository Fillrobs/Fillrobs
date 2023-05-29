# Generated by Django 2.2.16 on 2021-05-11 15:57

import common.fields
from django.db import migrations, models
import django.db.models.deletion
import driven_apps.common.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0060_role_group_types'),
        ('servicecatalog', '0071_set_slug_for_service_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlueprintBasedModulePolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The user-specified name of this Module Policy.', max_length=255)),
                ('description', models.TextField(blank=True, help_text='The description text for this Module Policy.', null=True)),
                ('policy_template', common.fields.TemplatableField(help_text='The template responsible for all aspects of this Module Policy.', max_length=65536)),
                ('blueprint', models.ForeignKey(help_text='The Blueprint that encapsulates all business logic for the module of the Module Policy.', on_delete=django.db.models.deletion.PROTECT, to='servicecatalog.ServiceBlueprint')),
                ('workspace', models.ForeignKey(help_text='Workspace URL', on_delete=django.db.models.deletion.PROTECT, to='accounts.Group')),
            ],
            options={
                'verbose_name': 'Module Policy',
                'verbose_name_plural': 'Module Policies',
                'db_table': 'module_policies',
                'ordering': ['-id'],
            },
            bases=(models.Model, driven_apps.common.mixins.RoleBasedHalFilteringMixin),
        ),
        migrations.AddConstraint(
            model_name='blueprintbasedmodulepolicy',
            constraint=models.UniqueConstraint(fields=('name',), name='module_policy_name_unique'),
        ),
    ]
