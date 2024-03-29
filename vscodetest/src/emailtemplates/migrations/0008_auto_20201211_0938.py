# Generated by Django 2.2.16 on 2020-12-11 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailtemplates', '0007_update_links_in_2_templates_20200925_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='from_address',
            field=models.CharField(blank=True, default='', help_text="Specify as: 'Full Name &lt;email@address>'<br/>Defaults to: 'no-reply@site.domain'", max_length=320, verbose_name='From address'),
        ),
    ]
