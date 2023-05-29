# Generated by Django 2.2.16 on 2021-03-01 18:03

from django.db import migrations


class Migration(migrations.Migration):
    def set_service_item_slugs(apps, schema_editor):
        model_slug_prefix = {
            "ProvisionServerServiceItem": "server",
            "BlueprintServiceItem": "blueprint",
            "RunCloudBoltHookServiceItem": "plugin",
            "RunRemoteScriptHookServiceItem": "script",
            "CopyFileActionServiceItem": "copy",
            "RunWebHookServiceItem": "webhook",
            "RunEmailHookServiceItem": "email",
            "RunTerraformPlanHookServiceItem": "terraform",
            "LoadBalancerServiceItem": "loadbalancer",
            "NetworkServiceItem": "network",
            "InstallPodServiceItem": "pod",
            "RunFlowHookServiceItem": "workflow",
            "TearDownServiceItem": "teardown",
        }

        for model, slug_prefix in model_slug_prefix.items():
            ServiceItem = apps.get_model('servicecatalog', model)
            for row in ServiceItem.objects.all():
                row.slug = f"{slug_prefix}-{row.global_id}"
                row.save()

    dependencies = [
        ('servicecatalog', '0070_service_item_add_slug'),
    ]

    operations = [
        migrations.RunPython(set_service_item_slugs, migrations.RunPython.noop),
    ]
