# Generated by Django 2.2.10 on 2020-09-04 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dns', '0003_microsoftdnspolicy'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlueCatDnsPolicy',
            fields=[
                ('dnspolicy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dns.DnsPolicy')),
            ],
            options={
                'db_table': 'dns_policies_bluecat',
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('dns.dnspolicy',),
        ),
    ]