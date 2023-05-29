from django.apps import apps
from django.db import migrations, connection

# Since this is a migration to remove an app that may or may not exist in
# the database, we can not use any of the normal DeleteModel, etc, everything
# has to be done explicitly through SQL. And if the table to remove does
# not exist we don't want to throw an error.  For that reason, and to help
# prevent errors during reverse migrations, the deleted tables are added back
# in the reverse_sql attribute. The intention of this is not to make the feature
# usable

APP_TO_REMOVE = "centurylink"


def get_id_to_remove(apps, schema_editor):
    ResourceTechnology = apps.get_model('resourcehandlers', 'ResourceTechnology')
    if ResourceTechnology.objects.filter(name="CenturyLink Cloud").exists():
        return ResourceTechnology.objects.get(name="CenturyLink Cloud").id
    else:
        return -1


def remove_centurylink_networks(apps, schema_editor):
    ResourceNetwork = apps.get_model('resourcehandlers', 'ResourceNetwork')
    if ResourceNetwork.objects.filter(real_type__model="ctlnetwork").exists():
        ResourceNetwork.objects.filter(real_type__model="ctlnetwork").delete()


def remove_centurylink_from_technology(apps, schema_editor):
    ResourceTechnology = apps.get_model('resourcehandlers', 'ResourceTechnology')
    if ResourceTechnology.objects.filter(name="CenturyLink Cloud").exists():
        ResourceTechnology.objects.filter(name="CenturyLink Cloud").delete()


def remove_centurylink_resource_handler(apps, schema_editor):
    ResourceHandlers = apps.get_model('resourcehandlers', 'ResourceHandler')
    if ResourceHandlers.objects.filter(resource_technology_id=get_id_to_remove(apps, schema_editor)).exists():
        ResourceHandlers.objects.filter(resource_technology_id=get_id_to_remove(apps, schema_editor)).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('resourcehandlers', '0023_retire_terremark'),
    ]

    # We are dynamically building the operations array to avoid deletions from
    # tables that don't exist
    operations = []

    # Query all table names in the db so we can add appropriate DELETES/DROPS
    all_tables = connection.introspection.table_names()

    if 'centurylink_ctlresourcehandler_networks' in all_tables:
        operations.append(migrations.RunSQL(
            sql=['DELETE FROM centurylink_ctlresourcehandler_networks;', ],
            reverse_sql=[],)
        )
    operations.append(migrations.RunSQL(
        sql=['DROP TABLE IF EXISTS centurylink_ctlresourcehandler_networks CASCADE;'],
        reverse_sql=[""" DROP TABLE IF EXISTS centurylink_ctlresourcehandler_networks CASCADE;
            CREATE TABLE `centurylink_ctlresourcehandler_networks` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `ctlresourcehandler_id` int(11) NOT NULL,
            `ctlnetwork_id` int(11) NOT NULL,
            PRIMARY KEY (`id`));
        """],)
    )

    if 'centurylink_ctlnetwork' in all_tables:
        operations.append(migrations.RunSQL(
            sql=['DELETE FROM centurylink_ctlnetwork;', ],
            reverse_sql=[], )
        )
    operations.append(migrations.RunSQL(
        sql=['DROP TABLE IF EXISTS centurylink_ctlnetwork CASCADE;'],
        reverse_sql=[""" DROP TABLE IF EXISTS centurylink_ctlnetwork CASCADE;
            CREATE TABLE `centurylink_ctlnetwork` (
            `resourcenetwork_ptr_id` int(11) NOT NULL,
            `uuid` varchar(36) NOT NULL,
            PRIMARY KEY (`resourcenetwork_ptr_id`));
        """], )
    )

    # This is a lecacy table and only impacts old installations of CloudBolt that was not cleaned up when depracated.
    # There is no reverse SQL for this because we do not want to create this table since it is no longer part of the product.
    operations.append(migrations.RunSQL(
        sql=["DROP TABLE IF EXISTS centurylink_ctlresourcehandler_os_build_attributes CASCADE;"],
        reverse_sql=[],
    ))

    if 'centurylink_ctlosbuildattribute' in all_tables:
        operations.append(migrations.RunSQL(
            sql=['DELETE FROM centurylink_ctlosbuildattribute;', ],
            reverse_sql=[], )
        )

    operations.append(migrations.RunSQL(
        sql=['DROP TABLE IF EXISTS centurylink_ctlosbuildattribute CASCADE;'],
        reverse_sql=["""  DROP TABLE IF EXISTS centurylink_ctlosbuildattribute CASCADE;
            CREATE TABLE `centurylink_ctlosbuildattribute` (
            `osbuildattribute_ptr_id` int(11) NOT NULL,
            `total_disk_size` decimal(10,4) DEFAULT NULL,
            PRIMARY KEY (`osbuildattribute_ptr_id`));
        """], )
    )

    if 'centurylink_ctlserverinfo' in all_tables:
        operations.append(migrations.RunSQL(
            sql=['DELETE FROM centurylink_ctlserverinfo;', ],
            reverse_sql=[],)
        )
    operations.append(migrations.RunSQL(
        sql=['DROP TABLE IF EXISTS centurylink_ctlserverinfo CASCADE;'],
        reverse_sql=["""  DROP TABLE IF EXISTS centurylink_ctlserverinfo CASCADE;
            CREATE TABLE `centurylink_ctlserverinfo` (
            `server_id` int(11) NOT NULL,
            `location_id` varchar(50) NOT NULL,
            `ctl_server_id` varchar(50) NOT NULL,
            `ctl_server_uuid` varchar(50) NOT NULL,
            PRIMARY KEY (`server_id`));
        """],)
    )

    if 'centurylink_ctlresourcehandler' in all_tables:
        operations.append(migrations.RunSQL(
            sql=['DELETE FROM centurylink_ctlresourcehandler;', ],
            reverse_sql=[],)
        )
    operations.append(migrations.RunSQL(
        sql=['DROP TABLE IF EXISTS centurylink_ctlresourcehandler CASCADE;'],
        reverse_sql=["""  DROP TABLE IF EXISTS centurylink_ctlresourcehandler CASCADE;
            CREATE TABLE `centurylink_ctlresourcehandler` (
            `resourcehandler_ptr_id` int(11) NOT NULL,
            PRIMARY KEY (`resourcehandler_ptr_id`));
        """],)
    )

    # Letting Python handle deletions of models that will still exist
    operations.append(migrations.RunPython(remove_centurylink_networks, noop))
    operations.append(migrations.RunPython(remove_centurylink_resource_handler, noop))
    operations.append(migrations.RunPython(remove_centurylink_from_technology, noop))

    # These calls shouldn't need customizing
    operations.append(migrations.RunSQL(
        sql=[f"DELETE FROM django_migrations where app='{APP_TO_REMOVE}';"],
        reverse_sql=[],)
    )
    if 'auth_permission' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM auth_permission WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'django_admin_log' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM django_admin_log WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'alerts_alertchannel' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM alerts_alertchannel WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'cbhooks_orchestrationhook' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM cbhooks_orchestrationhook WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'connectors_connectorconf' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM connectors_connectorconf WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'containerorchestrators_containerorchestrator' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM containerorchestrators_containerorchestrator WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'containerorchestrators_containerresource' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM containerorchestrators_containerresource WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'cscv_cittest' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM cscv_cittest WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'dataprotection_dataprotection' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM dataprotection_dataprotection WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'dns_policies' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM dns_policies WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'endpoints' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM endpoints WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'externalcontent_osbuildattribute' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM externalcontent_osbuildattribute WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'externalcontent_vendorapplication' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM externalcontent_vendorapplication WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'history_historymodel' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM history_historymodel WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'infrastructure_disk' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM infrastructure_disk WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'infrastructure_diskstorage' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM infrastructure_diskstorage WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'infrastructure_servernetworkcard' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM infrastructure_servernetworkcard WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'ipam_availableipamnetwork' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM ipam_availableipamnetwork WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'ipam_ipam' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM ipam_ipam WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'ipam_ipamnetwork' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM ipam_ipamnetwork WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'ipam_policy' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM ipam_policy WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'itsm_itsm' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM itsm_itsm WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'jobs_cfvchangeparameters' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM jobs_cfvchangeparameters WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'jobs_jobparameters' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM jobs_jobparameters WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'jobs_recurringjob' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM jobs_recurringjob WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'network_virtualization_networkvirtualization' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM network_virtualization_networkvirtualization WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'networks_loadbalancer' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM networks_loadbalancer WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'nsx_t_nsxtlogicalroutergateway' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM nsx_t_nsxtlogicalroutergateway WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'nsx_t_nsxttransportzone' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM nsx_t_nsxttransportzone WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'orchestrationengines_orchestrationengine' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM orchestrationengines_orchestrationengine WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'orders_actionjoborderitem' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM orders_actionjoborderitem WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'provisionengines_provisionengine' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM provisionengines_provisionengine WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'resourcehandlers_resourcehandler' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM resourcehandlers_resourcehandler WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'reversion_version' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM reversion_version WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'servicecatalog_serviceitem' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM servicecatalog_serviceitem WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'siem_siemprovider' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM siem_siemprovider WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'sso_basessoprovider' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM sso_basessoprovider WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'taggit_taggeditem' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM taggit_taggeditem WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'tags_taggeditem' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM tags_taggeditem WHERE content_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'utilities_sshkey' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM utilities_sshkey WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )
    if 'vra_policies' in all_tables:
        operations.append(migrations.RunSQL(
            sql=[f"DELETE FROM vra_policies WHERE real_type_id in (SELECT id FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}');"],
            reverse_sql=[],)
        )

    operations.append(migrations.RunSQL(
        sql=[f"DELETE FROM django_content_type WHERE app_label = '{APP_TO_REMOVE}';"],
        reverse_sql=[],)
    )
