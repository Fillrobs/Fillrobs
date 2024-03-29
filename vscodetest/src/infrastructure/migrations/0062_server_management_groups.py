# Generated by Django 3.2.5 on 2021-10-07 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0061_userprofile_legal_notice_seen'),
        ('infrastructure', '0061_merge_20210823_0019'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='management_groups',
            field=models.ManyToManyField(blank=True, help_text='Optionally select additional Groups used to provide more Users with permission to manage this Server. These Groups do not impact anything else, such as reports.', related_name='servers_with_management', to='accounts.Group', verbose_name='Management Groups'),
        ),
    ]
