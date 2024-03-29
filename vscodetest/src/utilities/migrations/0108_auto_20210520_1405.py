# Generated by Django 2.2.16 on 2021-05-20 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0107_associate_sshkeys_with_cfvs_20210520_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sshkey',
            name='key_reference',
            field=models.ForeignKey(help_text='The CustomFieldValue used internally to store the reference to the SSHKey that appears on the order form and elsewhere in the UI. For RH-specific keys, matches the name that comes from the Resource Handler.', on_delete=django.db.models.deletion.PROTECT, related_name='sshkey', to='orders.CustomFieldValue'),
        ),
    ]
