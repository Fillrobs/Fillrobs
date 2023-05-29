# Generated by Django 2.2.10 on 2020-02-28 18:37

import authentication.mixins
import cb_secrets.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0048_randomize_nonces'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSSOProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Give this single sign-on provider a name that will be displayed to users.', max_length=80, unique=True)),
                ('name_id_format', models.CharField(choices=[('urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified', 'Unspecified'), ('urn:oasis:names:tc:SAML:2.0:nameid-format:persistent', 'Persistent'), ('urn:oasis:names:tc:SAML:2.0:nameid-format:transient', 'Transient'), ('urn:oasis:names:tc:SAML:2.0:nameid-format:entity', 'Entity'), ('urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress', 'Email Address'), ('urn:oasis:names:tc:SAML:2.0:nameid-format:encrypted', 'Encrypted')], default='urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified', help_text='Defines the name identifier format supported by the IdP.', max_length=64, verbose_name='Name ID Format')),
                ('_required_attributes', models.CharField(blank=True, default='email,username', help_text='The combination of attributes that this SP will use for verifying a User that is sent from the IdP', max_length=512, verbose_name='Required Attributes')),
                ('private_key_file', cb_secrets.fields.EncryptedTextField(blank=True, help_text='If not provided, a Private Key will be generated.', null=True, verbose_name='Private Key')),
                ('public_key_file', cb_secrets.fields.EncryptedTextField(blank=True, help_text='If not provided, a Public Key will be generated.', null=True, verbose_name='Public Key')),
                ('metadata_source', models.CharField(choices=[('URL', 'Metadata URL'), ('File', 'Metadata File'), ('Text', 'Metadata Text')], default='URL', max_length=8, verbose_name='Configure Using')),
                ('metadata_file', cb_secrets.fields.EncryptedTextField(blank=True, null=True, verbose_name='IdP Metadata')),
                ('valid_for', models.IntegerField(default=24, help_text='How many hours this configuration is expected to be accurate.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Metadata Validity Limit')),
                ('accepted_time_diff', models.IntegerField(default=60, help_text='Maximum time difference between SP and IdP SSO servers, in seconds.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Accepted Time Difference')),
                ('sign_requests', models.BooleanField(default=True, help_text='If selected, indicates that the SP will send signed requests to the IdP.', verbose_name='Sign Requests')),
                ('force_authn', models.BooleanField(default=True, help_text='If selected, indicates that the IdP must authenticate the presenter directly rather than rely on a previous security context.', verbose_name='Force Authentication')),
                ('want_assertions_signed', models.BooleanField(default=True, help_text='If selected, indicates that the IdP should sign the assertion in an authentication response.', verbose_name='Assertion Signed')),
                ('want_response_signed', models.BooleanField(default=True, help_text='If selected, indicates that the IdP should sign the authentication response.', verbose_name='Response Signed')),
                ('allow_unsolicited', models.BooleanField(default=True, help_text='If selected, the SP will consume SAML Responses for which it has not sent a respective SAML Authentication Request.', verbose_name='Allow Unsolicited')),
                ('allow_unknown_attributes', models.BooleanField(default=True, help_text='If selected, allow extra attributes to be sent in the SAML Response to the SP beyond what is expected from the SAML Attribute Mapping.', verbose_name='Allow Unknown Attributes')),
                ('create_unknown_user', models.BooleanField(default=True, help_text='If selected, new users will be created upon receipt from the IdP.', verbose_name='Create Unknown Users')),
                ('debug', models.BooleanField(default=False, help_text='If selected, debug information will be sent to the log file.', verbose_name='Debug')),
                ('user_attribute_email', models.CharField(help_text="Key for the IdP's 'email' attribute.", max_length=80, verbose_name='Email Attribute Name')),
                ('user_attribute_given_name', models.CharField(help_text="Key for the IdP's 'given name' attribute.", max_length=80, verbose_name='Given Name Attribute Name')),
                ('user_attribute_sn', models.CharField(help_text="Key for the IdP's 'surname' attribute.", max_length=80, verbose_name='Surname Attribute Name')),
                ('user_attribute_uid', models.CharField(help_text="Key for the IdP's 'user id' attribute.", max_length=80, verbose_name='User ID Attribute Name')),
                ('organization_name', models.CharField(blank=True, help_text="Simple name of this organization. Will be used in this Service Provider's metadata and when generating a certificate.", max_length=255, null=True, verbose_name='Organization Name')),
                ('organization_display_name', models.CharField(blank=True, help_text="Full name of this organization. Will be used in this Service Provider's metadata and when generating a certificate.", max_length=255, null=True, verbose_name='Organization Display Name')),
                ('organization_url', models.CharField(blank=True, help_text="Full URL associated with this organization. Will be used in this Service Provider's metadata and when generating a certificate.", max_length=255, null=True, verbose_name='Organization URL')),
                ('contact_person', models.ManyToManyField(blank=True, help_text="Limited to Users with the 'CB Admin' role.", limit_choices_to={'super_admin': True}, to='accounts.UserProfile', verbose_name='Contact Person')),
                ('real_type', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Base SSO Provider',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(authentication.mixins.FieldDefaultsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GenericSAMLProvider',
            fields=[
            ],
            options={
                'verbose_name': 'Generic SAML Provider',
                'abstract': False,
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sso.basessoprovider',),
        ),
        migrations.CreateModel(
            name='OktaSSOProvider',
            fields=[
            ],
            options={
                'verbose_name': 'Okta',
                'abstract': False,
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sso.basessoprovider',),
        ),
    ]