# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-16 16:52
from __future__ import unicode_literals

from django.db import migrations


base_templates = {
    'order-complete-for-recipient': {
        'name': 'Order Complete for Recipient',
        'subject': """
            Order #{{ order.id }} ({{ order.name|lower|default:"No name" }}) completed with you as recipient
            """,
        'body': """
            {% load helper_tags %}
            Order #{{ order.id }}, where {{ order.owner }} selected you as the recipient, has completed.
            {% if resource %}
                Deployed {{ resource.resource_type.label }} you now own:
                    * Name: {{ resource.name }}{% if resource.rate %}
                        Rate: {{ resource.rate_display }}{% endif %}
                        View it at {% site_link resource %}
            {% endif %}
            {% if servers %}
                Provisioned server{{ servers|pluralize }} you now own:
                {% for server in servers %}
                    * Hostname: {{ server.get_vm_name }}{% if server.ip %}
                        Primary IP: {{ server.ip }} {% endif %}{% if server.rate %}
                        Rate: {{ server.rate_display }}{% endif %}
                        View it at {% site_link server %}
                {% endfor%}
            {% endif %}
            """,
    },
}


def create_templates(apps, schema_editor):
    """
    For each of the template defined above, create or update on the slug
    and update the remaining fields. This will also default to not renamable,
    making the templates loaded through this migration un-deletable via the UI.
    We use this rather than cb_minimal to create OOTB email templates.
    """
    EmailTemplate = apps.get_model('emailtemplates', 'EmailTemplate')
    for slug, defaults in base_templates.items():
        EmailTemplate.objects.update_or_create(
            is_renamable=False,
            slug=slug,
            defaults=defaults
        )


class Migration(migrations.Migration):

    dependencies = [
        ('emailtemplates', '0003_auto_20171012_2009'),
    ]

    operations = [
        migrations.RunPython(create_templates, migrations.RunPython.noop),
    ]
