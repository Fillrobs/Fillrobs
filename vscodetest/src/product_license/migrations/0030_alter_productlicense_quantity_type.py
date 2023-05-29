# Generated by Django 3.2.5 on 2021-11-22 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_license', '0029_move_license_to_db'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlicense',
            name='quantity_type',
            field=models.CharField(choices=[('CPU_SOCKET', 'CPU_SOCKET'), ('MANAGED_OBJECT', 'MANAGED_OBJECT'), ('MODULE', 'MODULE'), ('SERVER', 'SERVER')], max_length=32),
        ),
    ]
