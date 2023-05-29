# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.validators
import django.db.models.deletion
import cb_secrets.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CBReleaseInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250, blank=True)),
                ('version', models.CharField(max_length=250, blank=True)),
                ('type', models.CharField(max_length=250, blank=True)),
                ('upgrader_url', models.URLField(blank=True)),
                ('release_notes_url', models.URLField(blank=True)),
                ('checksum', models.CharField(max_length=250, blank=True)),
                ('release_date', models.CharField(max_length=250, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConnectionInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='This is the identifier used by code in actions to look up this object or check its value', max_length=50)),
                ('ip', models.CharField(max_length=50, verbose_name='IP/Hostname')),
                ('port', models.IntegerField(blank=True, null=True, validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(max_length=10, blank=True)),
                ('username', models.CharField(max_length=250, blank=True)),
                ('password', cb_secrets.fields.EncryptedPasswordField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Connection Info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GlobalPreferences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('singleton', models.CharField(default='S', unique=True, max_length=2, editable=False)),
                ('help_url', models.URLField(help_text="Overrides the 'help' link in CB's navigation bar.", null=True, verbose_name='URL for site-specific help', blank=True)),
                ('default_redirect', models.CharField(default='/dashboard/', help_text="\n            URL to redirect users users to when they navigate to / on the CB\n            server.  Common examples are '/dashboard/' (the default),\n            '/services/', and '/servers/'.\n        ", max_length=255, verbose_name='Default redirect (web server needs to be restarted for this to take effect)', blank=True)),
                ('smtp_host', models.CharField(max_length=255, null=True, verbose_name='SMTP Host', blank=True)),
                ('smtp_port', models.IntegerField(default=25, null=True, verbose_name='SMTP Port', blank=True)),
                ('smtp_user', models.CharField(max_length=255, null=True, verbose_name='SMTP Username', blank=True)),
                ('smtp_password', cb_secrets.fields.EncryptedPasswordField(verbose_name='SMTP Password', blank=True)),
                ('smtp_use_tls', models.BooleanField(default=False, verbose_name='SMTP use TLS')),
                ('email_default_from_address', models.CharField(max_length=255, null=True, blank=True)),
                ('email_reminder_frequency_min', models.IntegerField(default=180, verbose_name='Reminder Email Frequency Limit (minutes)', validators=[common.validators.is_only_digits])),
                ('cbadmin_email', models.EmailField(help_text='Send failure reports to this e-mail address.', max_length=255, null=True, verbose_name='CB Admin E-mail', blank=True)),
                ('rate_time_unit', models.CharField(default='MONTH', max_length=10, choices=[('HOUR', 'hr'), ('DAY', 'day'), ('WEEK', 'wk'), ('MONTH', 'month'), ('YEAR', 'yr'), ('FLAT', 'one time cost')])),
                ('rate_currency_unit', models.CharField(default='$', help_text='Ex. \xc2\xa5, \xe2\x82\xac, \xc2\xa3, SEK, CHF, R$, $, etc', max_length=10)),
                ('check_ga_releases', models.BooleanField(default=True, verbose_name='Check GA releases')),
                ('check_rc_releases', models.BooleanField(default=False, verbose_name='Check RCs')),
                ('check_alpha_releases', models.BooleanField(default=False, verbose_name='Check Alpha releases')),
                ('a_la_carte_servers', models.BooleanField(default=True, help_text="If disabled, the 'New Server' buttons will not be shown (except to CB admins). This is useful if you want normal users to only request services, and not ad hoc servers.")),
                ('main_list_per_page', models.IntegerField(default=15, validators=[common.validators.is_only_digits])),
                ('sub_list_per_page', models.IntegerField(default=5, validators=[common.validators.is_only_digits])),
                ('navigation_scheme', models.CharField(default='LINKS', max_length=5, editable=False, choices=[('LINKS', 'Links'), ('ICONS', 'Icons')])),
                ('security_message', models.CharField(help_text='Enter security message, HTML tags ok, up to 1000 chars', max_length=1000, null=True, blank=True)),
                ('email_output_directory', models.CharField(help_text='If set, email will be output to files in this directory, rather than sent via SMTP.', max_length=50, null=True, blank=True)),
                ('enable_map_feature', models.BooleanField(default=False)),
                ('enable_license_feature', models.BooleanField(default=False, help_text='Enable license management feature', verbose_name='License management')),
                ('enable_dcs_feature', models.BooleanField(default=False, help_text='Enable data centers feature.', verbose_name='Data centers')),
                ('enable_social_feature', models.BooleanField(default=True, help_text='Enables CB users to post to social websites.', verbose_name='Social')),
                ('enable_console_feature', models.BooleanField(default=True, help_text='Enables users to get console on servers they have access to. For resource handlers that support console.', verbose_name='Console feature')),
                ('enable_remote_feature', models.BooleanField(default=False, help_text='Enables users to RDP/SSH to servers they have access to.', verbose_name='RDP/SSH feature')),
                ('enable_local_credentials_store', models.BooleanField(default=True, verbose_name='User authentication without an external backend', editable=False)),
                ('enable_google_authentication', models.BooleanField(default=False, help_text='\n            Enable user authentication via Google\'s API. See the <a\n            href="/static-6dbe029/docs//users-and-permissions.html#setting-up-google-authentication">\n            docs on setting up Google authentication</a> to learn about the\n            other required steps.\n            ', verbose_name='Google authentication')),
                ('restrict_new_environments', models.BooleanField(default=False, help_text='When new CB environments are created, instead of being available to all groups, restrict them to only the unassigned group (and thus do not show them in the order form until they are exposed to more groups).')),
                ('enforce_single_session', models.BooleanField(default=False, help_text='If a user logs in from a second location or browser, the initial session will be logged out.', verbose_name='Enforce single sessions for users')),
                ('reuse_historical_hostnames', models.BooleanField(default=True, help_text='When generating unique hostnames during server provisioning, reuse hostnames of servers that are no longer active.')),
                ('allow_approver_to_edit_pending_orders', models.BooleanField(default=False, help_text='Allow approvers to modify pending orders. Normally, orders that have been submitted are not editable.', verbose_name='Editable pending orders')),
                ('fast_track_decom', models.BooleanField(default=False, help_text='Start decommissioning jobs immediately instead of routing requests through the normal order approval process.', verbose_name='Fast Track Server Deletion')),
                ('show_rates_when_ordering', models.BooleanField(default=True, help_text='Display rate information when ordering servers, both a la carte and through a service.', verbose_name='Show rates when ordering')),
                ('run_quick_setup', models.BooleanField(default=True, help_text='Not yet implemented.  Once it is: If True, directs user to Quick Setup wizard.  After completing or skipping QS, this setting is set to False.', editable=False)),
                ('generic_error_message', models.TextField(help_text='A message that is shown on failed job pages, HTTP error\n        pages (500, 404, etc), and other pages where the user hit a problem.\n        This can be used to provide the user with contact info on how to get\n        support for CloudBolt within your company. ', blank=1)),
                ('inactivity_timeout_minutes', models.IntegerField(default=0, help_text='If set, log user out after this many minutes of inactivity.', null=True, blank=True)),
                ('server_table_columns', models.CharField(max_length=1000, null=True, blank=True)),
                ('group_cost_details_table_columns', models.CharField(max_length=1000, null=True, blank=True)),
                ('bypass_proxy_domains', models.TextField(help_text="A comma separated list of the domains for which CloudBolt should not attempt to use a proxy server to route the connections. These domain names are regular expressions and could also be represented as ipv4 IP addresses. Ex. '.*\\.internal\\.loc,192\\.168\\..*,my\\.domain\\.com'.", null=True, blank=True)),
                ('group_name_levels_to_show', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Global Preferences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LDAPUtility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(help_text='IP address of AD/LDAP server', max_length=50, verbose_name='IP Address')),
                ('port', models.IntegerField(default=389, help_text='Default ports: 389 (insecure) and 636 (secure).', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(default='ldap', max_length=10, choices=[('ldap', 'ldap'), ('ldaps', 'ldaps')])),
                ('version', models.CharField(default='3', max_length=3, verbose_name='LDAP Version', choices=[('2', 'Version 2'), ('3', 'Version 3')])),
                ('serviceaccount', models.CharField(default='', help_text='Account with sufficient privileges to retrieve users and may need to be able to join servers to the domain.  For AD, use the form <code>username@domain</code>', max_length=100, verbose_name='Account')),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(verbose_name='Password')),
                ('ldap_domain', models.CharField(max_length=50, verbose_name='Domain')),
                ('base_dn', models.CharField(max_length=200, verbose_name='Base DN')),
                ('ldap_filter', models.CharField(help_text='Additional filter for validating user.  Example: <code>memberOf=OU=CloudBolt,DC=organization,DC=com</code>. If you are not familiar with LDAP filter syntax, leave this empty.', max_length=400, null=True, verbose_name='Search Filter', blank=True)),
                ('disabled_filter', models.CharField(default='userAccountControl:1.2.840.113556.1.4.803:=2', max_length=100, blank=True, help_text='Optional query filter that returns only disabled users. Allows CloudBolt to identify disabled accounts.', null=True, verbose_name='Disabled User Filter')),
                ('ldap_username', models.CharField(help_text='LDAP attribute to map to username. In Active Directory, this should be <code>sAMAccountName</code>.', max_length=50, verbose_name='Username Field')),
                ('ldap_first', models.CharField(default='givenName', help_text='LDAP attribute to map to first name', max_length=50, verbose_name='Firstname Field')),
                ('ldap_last', models.CharField(default='sn', help_text='LDAP attribute to map to last name', max_length=50, verbose_name='Lastname Field')),
                ('ldap_mail', models.CharField(default='mail', max_length=50, blank=True, help_text='LDAP attribute to map to user email (leave blank if the AD/LDAP being used has no attribute for email)', null=True, verbose_name='Email Field')),
                ('email_format', models.CharField(help_text='Define an email format if email is not part of the AD/LDAP. Example: <code>{{ first }}.{{ last }}@{{ domain }}</code>.  Possible references are first, last, username, and domain.', max_length=100, null=True, blank=True)),
                ('auto_create_user', models.BooleanField(default=True, help_text='Any valid LDAP account will be able to log into CloudBolt and a local profile will be created. Privileges must still be granted to new users through membership in CloudBolt groups.')),
            ],
            options={
                'verbose_name_plural': 'LDAP Utilities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PKIUtility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username_regex', models.CharField(default='UID=(\\w+)', max_length=100, verbose_name='RegEx to extract username from certifcate DN')),
                ('first_regex', models.CharField(default='CN=(\\w+)', max_length=100, null=True, verbose_name='RegEx to extract first name from certificate DN', blank=True)),
                ('last_regex', models.CharField(default='CN=.* (\\w+)', max_length=100, null=True, verbose_name='RegEx to extract last name from certificate DN', blank=True)),
                ('email_regex', models.CharField(default='emailAddress=(\\w+@\\w+\\.\\w+)', max_length=100, null=True, verbose_name='RegEx to extract email from certificate DN', blank=True)),
                ('email_format', models.CharField(max_length=100, null=True, verbose_name='Define an email\n        format if email is not part of the certificate.  For instance: {{ first\n        }}.{{ last }}@{{ domain }}.  Possible references are first, last, username,\n        and domain.', blank=True)),
                ('new_user_approver', models.ManyToManyField(related_name='create_as_approver', null=True, verbose_name='Auto-create as approver for', to='accounts.Group', blank=True)),
                ('new_user_environment_manager', models.ManyToManyField(related_name='create_as_environment_manager', null=True, verbose_name='Auto-create as environment manager for', to='accounts.Group', blank=True)),
                ('new_user_group_manager', models.ManyToManyField(related_name='create_as_group_manager', null=True, verbose_name='Auto-create as group manager for', to='accounts.Group', blank=True)),
                ('new_user_requestor', models.ManyToManyField(related_name='create_as_requestor', null=True, verbose_name='Auto-create as requestor for', to='accounts.Group', blank=True)),
            ],
            options={
                'verbose_name_plural': 'PKI Utilities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RADIUSUtility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('singleton', models.CharField(default='S', unique=True, max_length=2, editable=False)),
                ('server', models.CharField(max_length=50)),
                ('port', models.IntegerField(validators=[common.validators.is_only_digits])),
                ('secret', cb_secrets.fields.EncryptedPasswordField()),
            ],
            options={
                'verbose_name_plural': 'RADIUS Utilities',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='globalpreferences',
            name='default_ldap',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.LDAPUtility', help_text='Which LDAP server should be selected by default on the login page (if any).', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='globalpreferences',
            name='group_type_order_filter',
            field=models.ManyToManyField(related_name='group_types_that_can_order', verbose_name='Valid group types for Orders', to='accounts.GroupType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='globalpreferences',
            name='web_proxy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='Proxy server to use for outgoing connections (to public cloud providers like Azure, etc.)', null=True),
            preserve_default=True,
        ),
    ]
