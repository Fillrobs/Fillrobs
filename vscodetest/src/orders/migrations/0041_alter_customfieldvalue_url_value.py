# Generated by Django 3.2.3 on 2021-08-17 14:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0040_remove_customfieldvalue_tenant'),
    ]

    if "postgresql" in settings.DATABASES["default"]["ENGINE"]:
        operations = [
            migrations.RunSQL(
                sql=[("DROP INDEX url_value")],
                reverse_sql=[("CREATE INDEX url_value on orders_customfieldvalue(url_value)")],
            ),
            migrations.AlterField(
                model_name='customfieldvalue',
                name='url_value',
                field=models.URLField(blank=True, max_length=1024, null=True),
            ),
        ]
    else:
        operations = [
            migrations.RunSQL(
                sql=[("DROP INDEX url_value on orders_customfieldvalue")],
                reverse_sql=[("CREATE INDEX url_value on orders_customfieldvalue(url_value)")],
            ),
            migrations.AlterField(
                model_name='customfieldvalue',
                name='url_value',
                field=models.URLField(blank=True, max_length=1024, null=True),
            ),
        ]
