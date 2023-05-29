# Generated by Django 3.2.3 on 2021-09-22 17:09

from django.db import migrations


class Migration(migrations.Migration):

    def delete_netscaler_actions(apps, schema_editor):
        orchestration_action = apps.get_model("cbhooks", "OrchestrationHook")
        action_name_list = ["netscaler_construct_load_balancer", "netscaler_destroy_load_balancer", "netscaler_add_members_to_load_balancer", "netscaler_remove_members_from_load_balancer"]

        orchestration_action.objects.filter(name__in=action_name_list).delete()

    dependencies = [
        ('cbhooks', '0091_auto_20210820_2054'),
    ]

    operations = [
        migrations.RunPython(delete_netscaler_actions,  migrations.RunPython.noop)
    ]