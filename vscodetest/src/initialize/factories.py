from externalcontent.factories import OSFamilyFactory
from externalcontent.models import OSFamily
from infrastructure.factories import CustomFieldFactory
from infrastructure.models import Namespace


class CBMinimalFactory:
    def __init__(self, custom_fields=True, os_families=True):
        if custom_fields:
            self.__create_custom_fields()
        if os_families:
            self.__create_os_families()

    def __create_custom_fields(self):
        """
        Create CustomFields defined in cb_minimal.py
        """
        CustomFieldFactory(name="mem_size", label="Mem Size", type="DEC", required=True)
        CustomFieldFactory(name="cpu_cnt", label="CPUs", type="INT", required=True)
        CustomFieldFactory(
            name="disk_size", label="Disk Size", type="INT", required=False
        )
        CustomFieldFactory(name="new_disk_size", label="New Disk Size", type="INT")
        CustomFieldFactory(name="disk_X_size", label="Additional Disk Size", type="INT")
        CustomFieldFactory(
            name="extend_root_disk",
            label="Extend Primary Disk During Provisioning",
            type="BOOL",
        )
        CustomFieldFactory(
            name="link_clone", label="Provision as VMware Linked Clone", type="BOOL"
        )
        CustomFieldFactory(
            name="expiration_date",
            label="Expiration Date",
            type="DT",
            required=True,
            show_on_servers=True,
        )
        CustomFieldFactory(
            name="vmware_resourcepool", label="VMware Resource Pool", type="STR"
        )
        # Important! There is a copy of this in orders/migrations/0019_auto_20180119_1924.py
        # If you change this, make sure to change there and vice versa
        CustomFieldFactory(name="time_zone", label="Time Zone", type="STR")
        CustomFieldFactory(
            name="username", label="Username", type="STR", required=False
        )
        CustomFieldFactory(
            name="password", label="Password", type="PWD", required=False
        )

        # There is a copy of this in the migration
        # behavior_mapping/migrations/0007_replace_initial_password_global_default.py.
        # AND in orders/migrations/0019_auto_20180119_1924.py
        # If you change this, make sure to change it as well, and vice versa.
        CustomFieldFactory(
            name="new_password", label="New Password", type="PWD", required=True
        )
        CustomFieldFactory(name="os_license_key", label="OS License Key", type="STR")
        CustomFieldFactory(name="domain_to_join", label="Domain to Join", type="LDAP")
        CustomFieldFactory(name="dns_domain", label="DNS Domain", type="STR")
        CustomFieldFactory(name="domain_name_server", label="DNS Server", type="STR")
        CustomFieldFactory(
            name="vmware_datastore",
            label="VMware Datastore",
            type="STOR",
            required=True,
        )
        CustomFieldFactory(
            name="vmware_disk_type",
            label="VMware Disk Provisioning Type",
            type="STR",
            required=True,
        )
        CustomFieldFactory(
            name="vmware_cluster", label="VMware Cluster", type="STR", required=True
        )
        CustomFieldFactory(
            name="vmware_dns_search_path",
            label="VMware DNS search path",
            type="STR",
            required=False,
        )

        CustomFieldFactory(
            name="chef_environment",
            label="Chef Environment",
            type="STR",
            required=False,
            show_on_servers=True,
        )

        CustomFieldFactory(
            name="vm_customization_timeout",
            label="VM Customization Timeout",
            type="INT",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="post_prov_delay",
            label="Post Provisioning Delay",
            type="INT",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="hostname_template",
            label="Hostname Template",
            type="STR",
            required=True,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="tech_specific_script_execution",
            label="Use Tech-Specific Script Execution",
            type="BOOL",
            show_on_servers=True,
            available_all_servers=True,
        )

        CustomFieldFactory(
            name="supports_credssp",
            label="Supports CredSSP",
            type="BOOL",
            required=False,
        )

        CustomFieldFactory(
            name="gce_tags",
            label="GCE Network Tags",
            type="STR",
            required=True,
            show_on_servers=False,
        )

        # Important! This cf field dict is copied in orders/migrations/0019_auto_20180119_1924.py.
        # If changes are made, you'll need to change the migration.
        CustomFieldFactory(
            name="annotation",
            label="Annotation",
            type="TXT",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(name="sc_nic_0", label="NIC 1", type="NET", required=True)
        CustomFieldFactory(name="sc_nic_1", label="NIC 2", type="NET")
        CustomFieldFactory(name="sc_nic_2", label="NIC 3", type="NET")
        CustomFieldFactory(name="sc_nic_3", label="NIC 4", type="NET")
        CustomFieldFactory(name="sc_nic_4", label="NIC 5", type="NET")
        CustomFieldFactory(name="sc_nic_5", label="NIC 6", type="NET")
        CustomFieldFactory(name="sc_nic_6", label="NIC 7", type="NET")
        CustomFieldFactory(name="sc_nic_7", label="NIC 8", type="NET")
        CustomFieldFactory(name="sc_nic_8", label="NIC 9", type="NET")
        CustomFieldFactory(name="sc_nic_9", label="NIC 10", type="NET")

        CustomFieldFactory(
            name="disk_1_size",
            label="Size for Disk 2",
            type="INT",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="disk_2_size",
            label="Size for Disk 3",
            type="INT",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="disk_3_size",
            label="Size for Disk 4",
            type="INT",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="open_ports_tcp",
            label="Open TCP Ports",
            type="STR",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="open_ports_udp",
            label="Open UDP Ports",
            type="STR",
            required=False,
            show_on_servers=False,
        )

        CustomFieldFactory(
            name="os_services",
            label="OS Services",
            type="CODE",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="os_users",
            label="OS Users",
            type="CODE",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="os_disks_logical",
            label="OS Logical Disks",
            type="CODE",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="os_disks_physical",
            label="OS Physical Disks",
            type="CODE",
            required=False,
            show_on_servers=False,
        )
        CustomFieldFactory(
            name="os_partitions",
            label="OS Partitions",
            type="CODE",
            required=False,
            show_on_servers=False,
        )

        # we create these at CB install time so that we can write code like
        # "if svr.sc_nic_0_ip:" without having to worry about it throwing an
        # AttributeError
        # see https://www.pivotaltracker.com/story/show/64498334
        CustomFieldFactory(name="sc_nic_0_ip", label="NIC 1 IP", type="IP")
        CustomFieldFactory(name="sc_nic_1_ip", label="NIC 2 IP", type="IP")
        CustomFieldFactory(name="sc_nic_2_ip", label="NIC 3 IP", type="IP")
        CustomFieldFactory(name="sc_nic_3_ip", label="NIC 4 IP", type="IP")
        CustomFieldFactory(name="sc_nic_4_ip", label="NIC 5 IP", type="IP")
        CustomFieldFactory(name="sc_nic_5_ip", label="NIC 6 IP", type="IP")
        CustomFieldFactory(name="sc_nic_6_ip", label="NIC 7 IP", type="IP")
        CustomFieldFactory(name="sc_nic_7_ip", label="NIC 8 IP", type="IP")
        CustomFieldFactory(name="sc_nic_8_ip", label="NIC 9 IP", type="IP")
        CustomFieldFactory(name="sc_nic_9_ip", label="NIC 10 IP", type="IP")

        CustomFieldFactory(
            name="server_cnt", label="Max. Servers Allowed Per Handler", type="INT"
        )
        CustomFieldFactory(
            name="quantity",
            label="Quantity",
            type="INT",
            required=False,
            show_on_servers=False,
            # global_constraints={'minimum': 0},
        )

        CustomFieldFactory(
            name="c2_skip_network_conf", label="Skip Network Configuration", type="BOOL"
        )

        CustomFieldFactory(
            name="skip_rh_hostname_validation",
            label="Skip RH Hostname Validation",
            type="BOOL",
        )

        advanced_networking = Namespace.objects.create(name="advanced_networking")
        CustomFieldFactory(
            name="nsx_scope",
            label="NSX Transport Zone",
            type="NSXS",
            namespace=advanced_networking,
        )
        CustomFieldFactory(
            name="nsx_edge",
            label="NSX Edge",
            type="NSXE",
            namespace=advanced_networking,
        )

        CustomFieldFactory(
            name="key_name", label="Key pair name", type="STR", required=True
        )

        CustomFieldFactory(
            name="server_lock",
            label="Server Lock",
            type="STR",
            required=False,
            show_on_servers=True,
            available_all_servers=True,
        )

        CustomFieldFactory(
            name="nla_for_rdp",
            label="Use NLA for RDP",
            type="BOOL",
            show_on_servers=True,
        )

        CustomFieldFactory(name="license_type", label="Azure License Type", type="STR")

        CustomFieldFactory(
            name="skip_security_group",
            label="Skip Security Group Creation",
            type="BOOL",
        )

        CustomFieldFactory(name="power_schedule", label="Power Schedule", type="STR")

        CustomFieldFactory(
            name="vmware_sysprep_file",
            label="Sysprep Answer File",
            type="CODE",
            required=True,
        )

    def __create_os_families(self):
        """
        Create OSFamilies defined in cb_minimal.py
        """
        os_families = [
            {"name": "Linux", "parent": None},
            {"name": "Windows", "parent": None},
            {"name": "Unix", "parent": None},
            {"name": "Red Hat", "parent": "Linux"},
            {"name": "Fedora", "parent": "Linux"},
            {"name": "Ubuntu", "parent": "Linux"},
            {"name": "CentOS", "parent": "Linux"},
            {"name": "CoreOS", "parent": "Linux"},
            {"name": "Oracle Enterprise Linux", "parent": "Linux"},
            {"name": "ESXi", "parent": "Linux"},
            {"name": "SUSE", "parent": "Linux"},
            {"name": "Debian", "parent": "Linux"},
            {"name": "Amazon Linux", "parent": "Linux"},
            {"name": "macOS", "parent": "Unix"},
            {"name": "Solaris", "parent": "Unix"},
        ]
        for family in os_families:
            name, parent = family.values()
            if parent:
                parent_obj = OSFamily.objects.get(name=parent)
                OSFamilyFactory(name=name, parent=parent_obj)
                OSFamilyFactory(name=name.lower(), parent=parent_obj)
            else:
                OSFamilyFactory(name=name)
                OSFamilyFactory(name=name.lower())
