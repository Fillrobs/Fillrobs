# Generated by Django 2.2.10 on 2020-04-28 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0012_merge_20200410_0734'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openstackimage',
            options={'verbose_name': 'OpenStackImage'},
        ),
    ]