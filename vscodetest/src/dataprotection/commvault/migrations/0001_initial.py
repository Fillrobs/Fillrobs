from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dataprotection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommVaultDataProtection',
            fields=[
                ('dataprotection_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dataprotection.DataProtection')),
            ],
            options={
                'verbose_name': 'CommVault Data Protection',
                'abstract': False,
            },
            bases=('dataprotection.dataprotection',),
        ),
    ]
