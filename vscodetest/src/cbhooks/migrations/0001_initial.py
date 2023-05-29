# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.validators
import files.models
import django.db.models.deletion
import cb_secrets.fields
import common.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('infrastructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HookInput',
            fields=[
                ('customfield_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.CustomField', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('infrastructure.customfield',),
        ),
        migrations.CreateModel(
            name='HookMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('should_execute', models.NullBooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HookPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Should never change after the first time this type appears in the CB data set, as other things will depend on it.', unique=True, max_length=255)),
                ('label', models.CharField(help_text='A user-visible label for this hook point. Can be changed without impacting functionality.', unique=True, max_length=255)),
                ('description', models.TextField(help_text='Explains when this hook point is executed', null=True, blank=True)),
                ('job_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='Job Type', choices=[('provision', 'Provision Server'), ('decom', 'Delete Server'), ('healthcheck', 'Health Check'), ('expire', 'Expire'), ('servermodification', 'Server Modification'), ('install_service', 'Install Service'), ('install_pod', 'Install Pod'), ('installapplications', 'Install Applications'), ('uninstallapplications', 'Uninstall Applications'), ('syncvms', 'Synchronize VMs from Resource Handlers'), ('sync_svrs_from_pe', 'Synchronize servers from Provision Engines'), ('functionaltest', 'Continuous Infrastructure Testing'), ('runautomations', 'Execute Rules'), ('runautomationactions', 'Execute Rule Actions'), ('sync_users_from_ldap', 'Synchronize users from an LDAP server'), ('run_flow', 'Orchestration Flow'), ('install_apps_with_connector', 'Install Applications with Configuration Manager'), ('manage_nics', 'Manage NICs'), ('orchestration_hook', 'Orchestration Action'), ('delete_snapshots', 'Delete Snapshots')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HookPointAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(help_text='Explains the purpose of this action trigger', null=True, blank=True)),
                ('enabled', models.BooleanField(default=False)),
                ('run_seq', models.IntegerField(help_text='Order in which actions for a particular hook pointwill be run.', null=True, blank=True)),
                ('run_on_statuses', models.CharField(default='', help_text='Determines which statuses from the main job should cause a post-job hook to run', max_length=255, verbose_name='Statuses to Run On', blank=True)),
            ],
            options={
                'ordering': ['run_seq', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrchestrationHook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(help_text='Explains the steps performed by this hook', null=True, blank=True)),
                ('shared', models.BooleanField(default=False, help_text='Make this action available for reuse by others. Useful when it is of a general nature.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowHook',
            fields=[
                ('orchestrationhook_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.OrchestrationHook', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('cbhooks.orchestrationhook',),
        ),
        migrations.CreateModel(
            name='EmailHook',
            fields=[
                ('orchestrationhook_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.OrchestrationHook', on_delete=models.CASCADE)),
                ('subject', models.CharField(max_length=256, null=True, blank=True)),
                ('body', models.TextField(help_text="The body of the email to send. Uses the same format as <a href=/static-6dbe029/docs/admin/order-form-customization.html#using-hostname-templates>CloudBolt's hostname templates</a>.", null=True, blank=True)),
                ('from_address', models.CharField(help_text="The address from which the email will be sent. If not specified, CB Admin email from Admin -> Email settings will be used. Uses the same format as <a href=/static-6dbe029/docs/admin/order-form-customization.html#using-hostname-templates>CloudBolt's hostname templates</a>.", max_length=256, null=True, blank=True)),
                ('send_to_address', models.CharField(help_text='A comma separated list of recipients.', max_length=256, null=True, blank=True)),
                ('send_to_job_owner', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('cbhooks.orchestrationhook',),
        ),
        migrations.CreateModel(
            name='CloudBoltHook',
            fields=[
                ('orchestrationhook_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.OrchestrationHook', on_delete=models.CASCADE)),
                ('module_file', models.FileField(help_text='For more information on the requirements for CloudBolt plug-ins see the <a target="cbhelp" href="/static/docs/advanced/orchestration-actions/cloudbolt-plugins.html">CloudBolt Documentation.</a>', max_length=255, null=True, upload_to='hooks', blank=True)),
                ('source_code_url', models.TextField(help_text='\n            Code will be fetched from here before action is run. E.g. URL\n            (without any authentication tokens) to the raw file hosted on your\n            github.com repository or on the <span class="cb-forge-btn"><a class="link no-tooltip-affordance"\n            href="https://github.com/CloudBoltSoftware/cloudbolt-forge"\n            target="_blank"\n            data-toggle="tooltip"\n            data-placement="bottom"\n            title="View and use actions shared by the CloudBolt community (new window)">\n             CloudBolt Forge \n            <i class="glyphicon glyphicon-fire"></i></a></span>\n.  For details \n<a href="/static/docs/advanced/orchestration-actions/actions.html#external-source-code"\n    target="help"\n    class="no-tooltip-affordance"\n    data-toggle="tooltip"\n    data-html="true"\n    title="Learn more in the CloudBolt Docs <p>(new window)</p>">\n     see the docs \n    <i class="icon-help"></i>\n</a>\n.\n            ', null=True, verbose_name='URL for source code', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cbhooks.orchestrationhook', files.models.ExternalSourceCodeMixin),
        ),
        migrations.CreateModel(
            name='RemoteScriptHook',
            fields=[
                ('orchestrationhook_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.OrchestrationHook', on_delete=models.CASCADE)),
                ('script_file', models.FileField(help_text='Path to the script for this hook', max_length=255, null=True, upload_to='hooks', blank=True)),
                ('execution_timeout', models.IntegerField(default=120, help_text='Timeout (in seconds) before exiting out of the remotescript execution with an error', validators=[common.validators.is_only_digits])),
                ('commandline_args', models.CharField(help_text='Any commandline arguments to pass to the script as it is run on the guest operating system. Uses the same format as <a target="cbhelp" href=/static-6dbe029/docs/order-form-customization.html#using-hostname-templates>CloudBolt\'s hostname templates</a>.', max_length=256, null=True, blank=True)),
                ('source_code_url', models.TextField(help_text='\n            Code will be fetched from here before action is run. E.g. URL\n            (without any authentication tokens) to the raw file hosted on your\n            github.com repository or on the <span class="cb-forge-btn"><a class="link no-tooltip-affordance"\n            href="https://github.com/CloudBoltSoftware/cloudbolt-forge"\n            target="_blank"\n            data-toggle="tooltip"\n            data-placement="bottom"\n            title="View and use actions shared by the CloudBolt community (new window)">\n             CloudBolt Forge \n            <i class="glyphicon glyphicon-fire"></i></a></span>\n.  For details \n<a href="/static/docs/advanced/orchestration-actions/actions.html#external-source-code"\n    target="help"\n    class="no-tooltip-affordance"\n    data-toggle="tooltip"\n    data-html="true"\n    title="Learn more in the CloudBolt Docs <p>(new window)</p>">\n     see the docs \n    <i class="icon-help"></i>\n</a>\n.\n            ', null=True, verbose_name='URL for source code', blank=True)),
                ('run_with_sudo', models.BooleanField(default=False, help_text='Configure this script to run with sudo on Linux servers.')),
            ],
            options={
                'abstract': False,
            },
            bases=('cbhooks.orchestrationhook', files.models.ExternalSourceCodeMixin, common.mixins.HasCustomFieldValuesMixin),
        ),
        migrations.CreateModel(
            name='RunHookInputMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_classes', models.CharField(default='', help_text="\n        Can be used to add an icon on the button. Must correspond to an icon name that\n        CloudBolt has. Ex. 'icon-delete', 'glyphicon glyphicon-time', 'fas fa-heartbeat'. For\n        more examples, see\n        <a href='http://fortawesome.github.io/Font-Awesome/icons/'>Font Awesome</a> and\n        <a href='http://getbootstrap.com/components/'>Glyphicons</a>", max_length=255, blank=True)),
                ('enabled', models.BooleanField(default=True)),
                ('label', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_classes', models.CharField(default='', help_text="\n        Can be used to add an icon on the button. Must correspond to an icon name that\n        CloudBolt has. Ex. 'icon-delete', 'glyphicon glyphicon-time', 'fas fa-heartbeat'. For\n        more examples, see\n        <a href='http://fortawesome.github.io/Font-Awesome/icons/'>Font Awesome</a> and\n        <a href='http://getbootstrap.com/components/'>Glyphicons</a>", max_length=255, blank=True)),
                ('enabled', models.BooleanField(default=True)),
                ('label', models.CharField(max_length=255)),
                ('dialog_message', models.TextField(default='', help_text='message to be shown in confirmation dialog after the action is chosen', blank=True)),
                ('submit_button_label', models.CharField(default='', help_text='text to be shown in confirmation dialog on the submit button', max_length=50, blank=True)),
                ('list_view_visible', models.BooleanField(default=True, help_text='Determines whether this action is a viableoption to list when running bulk service actions.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TriggerPoint',
            fields=[
                ('hookpoint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.HookPoint', on_delete=models.CASCADE)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=('cbhooks.hookpoint',),
        ),
        migrations.CreateModel(
            name='WebHook',
            fields=[
                ('orchestrationhook_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cbhooks.OrchestrationHook', on_delete=models.CASCADE)),
                ('url', models.TextField(help_text='A request will be made to this URL.', verbose_name='URL')),
                ('payload', models.TextField(default='', help_text='JSON formatted data to send in the request body.', blank=True)),
                ('authentication_method', models.CharField(default='basic', max_length=10, choices=[('none', 'No authentication'), ('basic', 'HTTP basic auth'), ('token', 'Token-based')])),
                ('http_method', models.CharField(default='post', max_length=10, verbose_name='HTTP method', choices=[('delete', 'DELETE'), ('get', 'GET'), ('head', 'HEAD'), ('patch', 'PATCH'), ('post', 'POST'), ('put', 'PUT')])),
                ('content_type', models.CharField(default='application/json', max_length=50, choices=[('application/x-www-form-urlencoded', 'WWW-Form'), ('application/json', 'JSON'), ('application/xml', 'XML')])),
                ('auth_header_name', models.CharField(default='', help_text='If specified, CB will use token-based auth, adding a field with this name to the HTTP headers. Use either this or username, not both.', max_length=100, blank=True)),
                ('auth_header_value', models.CharField(default='', max_length=512, blank=True)),
                ('http_username', models.CharField(default='', help_text='If specified, CB will use basic HTTP auth. Use either this or username, not both.', max_length=100, verbose_name='Username', blank=True)),
                ('http_password', cb_secrets.fields.EncryptedPasswordField(default='', verbose_name='Password', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cbhooks.orchestrationhook',),
        ),
        migrations.AddField(
            model_name='triggerpoint',
            name='condition',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='triggerpoint',
            name='condition_input_mappings',
            field=models.ManyToManyField(to='cbhooks.RunHookInputMapping'),
            preserve_default=True,
        ),
    ]
