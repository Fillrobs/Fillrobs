from __future__ import unicode_literals
from __future__ import print_function
from jobs.models import SyncVMParameters, FunctionalTestParameters, TriggerParameters
from resourcehandlers.acropolis.models import AcropolisResourceHandler
from resourcehandlers.alibaba.models import AlibabaResourceHandler
from resourcehandlers.alibaba.alibaba_minimal import alibaba_hooks
from resourcehandlers.aws.models import AWSHandler

from resourcehandlers.azure_arm.models import AzureARMHandler
from resourcehandlers.gce.models import GCEHandler
from resourcehandlers.gcp.models import GCPHandler
from resourcehandlers.helion.models import HelionHandler
from resourcehandlers.maas.models import MaasResourceHandler
from resourcehandlers.openstack.models import OpenStackHandler
from resourcehandlers.oci.models import OCIResourceHandler
from resourcehandlers.outscale.models import OutscaleResourceHandler

from resourcehandlers.slayer.models import SlayerResourceHandler
from resourcehandlers.hyperv.models import HyperVResourceHandler
from resourcehandlers.scvmm.models import SCVMMHandler
from resourcehandlers.vcloud_director.models import VCDHandler
from resourcehandlers.vmware.models import VmwareDisk
from django.utils.translation import ugettext_lazy as _lazy

# Feature Switches ###
features = {}
features["use_features"] = True

# GLOBAL PREFERENCES ###
gp = {}
gp["smtp_host"] = ""
gp["smtp_port"] = None
gp["smtp_use_tls"] = False
gp["smtp_user"] = ""
gp["smtp_password"] = ""
gp["enable_social_feature"] = True

# CONTENT LIBRARY ####
content_library = {
    "name": "CloudBolt Content Library",
    "ip": "content.cloudbolt.app",
    "protocol": "https",
    "port": 443,
}

# CUSTOM FIELDS ###
# each custom field requires a name, label, and type.  options are optional
mem_size_cf = {"name": "mem_size", "label": "Mem Size", "type": "DEC", "required": True}
cpu_cnt_cf = {"name": "cpu_cnt", "label": "CPUs", "type": "INT", "required": True}
disk_size_cf = {
    "name": "disk_size",
    "label": "Disk Size",
    "type": "INT",
    "description": (
        "Used to calculate the expected rate of new servers. Additionally, "
        'during VMware provisioning, when the "Extend '
        'Primary Disk During Provisioning" parameter is true, the root disk is '
        "extended to this value."
    ),
    "required": False,
}
new_disk_size_cf = {"name": "new_disk_size", "label": "New Disk Size", "type": "INT"}
additional_disk_size_cf = {
    "name": "disk_X_size",
    "label": "Additional Disk Size",
    "type": "INT",
    "description": ("Used to constrain all additional disks added to VMs"),
}
extend_root_disk_cf = {
    "name": "extend_root_disk",
    "label": "Extend Primary Disk During Provisioning",
    "type": "BOOL",
    "description": (
        "If set to true, the primary disk on the server will be extended "
        "to the given disk size."
    ),
}
link_clone_cf = {
    "name": "link_clone",
    "label": "Provision as VMware Linked Clone",
    "type": "BOOL",
    "description": (
        "The newly provisioned server will share the virtual disk with its "
        "parent template and only deltas will be saved separately. Because of "
        "this, linked clones are provisioned very quickly. Requires the presence "
        "of a snapshot on the template and is not supported when provisioning "
        "to a NAS datastore."
    ),
}
expiration_date_cf = {
    "name": "expiration_date",
    "label": "Expiration Date",
    "type": "DT",
    "required": True,
    "show_on_servers": True,
}
vm_pool_cf = {
    "name": "vmware_resourcepool",
    "label": "VMware Resource Pool",
    "type": "STR",
}
# Important! There is a copy of this in orders/migrations/0019_auto_20180119_1924.py
# If you change this, make sure to change there and vice versa
time_zone_cf = {"name": "time_zone", "label": "Time Zone", "type": "STR"}
username_cf = {
    "name": "username",
    "label": "Username",
    "type": "STR",
    "required": False,
    "description": (
        "This is the user that CB will attempt to use to perform actions " "on a server"
    ),
}
password_cf = {
    "name": "password",
    "label": "Password",
    "type": "PWD",
    "required": False,
    "description": (
        "This is the password that CB will attempt to use, in conjunction "
        "with the username in the Username parameter, to perform actions "
        "on a server"
    ),
}
# IMPORTANT: There is a copy of this in the migration
# behavior_mapping/migrations/0007_replace_initial_password_global_default.py.
# AND in orders/migrations/0019_auto_20180119_1924.py
# If you change this, make sure to change it as well, and vice versa.
new_password_cf = {
    "name": "new_password",
    "label": "New Password",
    "type": "PWD",
    "required": True,
    "description": ("This is the password that CB will change the VM to use"),
}
os_license_key_cf = {"name": "os_license_key", "label": "OS License Key", "type": "STR"}
domain_cf = {"name": "domain_to_join", "label": "Domain to Join", "type": "LDAP"}
dns_domain_cf = {
    "name": "dns_domain",
    "label": "DNS Domain",
    "type": "STR",
    "description": (
        "The DNS domain that servers built with CB should use for DNS queries.  "
        "Will only be used if the 'Domain to Join' is not specified'."
    ),
}
domain_name_server_cf = {
    "name": "domain_name_server",
    "label": "DNS Server",
    "type": "STR",
    "description": (
        "DNS server IP address that servers built with CB "
        "should use for DNS queries. More than one may be specified, separated by "
        "commas."
    ),
}
vmware_datastore_cf = {
    "name": "vmware_datastore",
    "label": "VMware Datastore",
    "type": "STOR",
    "required": True,
}
vmware_datastore_minimum_freespace_cf = {
    "name": "vmware_ds_min_freespace",
    "label": "VMware Datastore Free Space",
    "type": "STR",
    "required": True,
    "description": (
        "Minimum free space required to allow disks to provision to a VMware Datastore. If free space is "
        "determined by a % of total space, there must be a '%' character in the value.  Without the '%' character, "
        "the value will be treated as a hard requirement of Available Space in Bytes. "
        "Example for % free space requirement (10 percent): 10% "
        "Example for fixed space requirement (500GB): 500000000000"
    ),
}
vmware_disk_controller_cf = {
    "name": "vmware_disk_controller",
    "label": "VMware Disk Controller",
    "type": "STR",
    "description": (
        "Stores the value of the BUS:UNIT for a VMware disk/Controller relationship."
    ),
}
vmware_disk_controller_label_cf = {
    "name": "vmware_disk_controller_label",
    "label": "VMware Disk Controller Type",
    "type": "STR",
    "description": "The Display type of a VMware Disk Controller",
}
vmware_disk_type_cf = {
    "name": "vmware_disk_type",
    "label": "VMware Disk Provisioning Type",
    "type": "STR",
    "required": True,
}
vmware_cluster_cf = {
    "name": "vmware_cluster",
    "label": "VMware Cluster",
    "type": "STR",
    "required": True,
}
vmware_dns_search_path = {
    "name": "vmware_dns_search_path",
    "label": "VMware DNS search path",
    "type": "STR",
    "required": False,
    "description": (
        "Adding a DNS search path improves performance when translating a machine "
        "name into an IP address. VMware provides a way to support this, by "
        "adding the search path to the GlobalIPSettings of the provisioned VM."
    ),
}

chef_environment_cf = {
    "name": "chef_environment",
    "label": "Chef Environment",
    "type": "STR",
    "required": False,
    "show_on_servers": True,
    "description": (
        "Used to join Chef Nodes to environments when CB " "provisions them"
    ),
}

ansible_run_timeout = {
    "name": "ansible_run_timeout",
    "label": "Ansible Run Timeout",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": ("Timeout in seconds for running Ansible playbooks"),
}

vm_customization_timeout_cf = {
    "name": "vm_customization_timeout",
    "label": "VM Customization Timeout",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Timeout in seconds to wait for server to report as fully ready, "
        "for Resource Handlers that have a mechanism to wait for readiness. "
        "Default if not set depends on Resource Handler."
    ),
}

post_prov_delay_cf = {
    "name": "post_prov_delay",
    "label": "Post Provisioning Delay",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Delay period in seconds after powering on a VM and waiting for "
        "VM customization (where applicable) to wait before continuing "
        "with the provisioning job"
    ),
}

hostname_template_cf = {
    "name": "hostname_template",
    "label": "Hostname Template",
    "type": "STR",
    "required": True,
    "show_on_servers": False,
    "description": (
        "A parameterized template for generating hostnames. If used, "
        "the hostname will not be required on the new server form. "
        "Ex. '{{ os_family.get_base_name|first|lower }}svr{{ environment.name|slice:\":3\" }}-00X'."
        " For more info, see the docs on hostname templates."
    ),
}

tech_specific_script_execution_cf = {
    "name": "tech_specific_script_execution",
    "label": "Use Tech-Specific Script Execution",
    "type": "BOOL",
    "show_on_servers": True,
    "available_all_servers": True,
    "description": (
        "By default, remote scripts will be run using any tech-specific script "
        "execution method that might be defined for a Resource Handler, such "
        "as VMware tools. The generic script execution of WinRM/SSH will be "
        "used for Resource Handlers that do not have a tech-specific script "
        "execution method. If you would like servers on Resource Handlers that have "
        "a tech-specific script execution method (such as VMware) to instead "
        "run with WinRM/SSH, set this parameter to False for those servers."
    ),
}

supports_credssp_cf = {
    "name": "supports_credssp",
    "label": "Supports CredSSP",
    "type": "BOOL",
    "required": False,
    "description": (
        "If set to True, remote scripts will be run against this server using "
        "CredSSP, as opposed to NTLM or Basic Auth. Server credentials will double "
        "encryped under the SPNEGO and TLS session keys. This setting also allows the "
        "domain credentials for this server to be delegated over multiple hops. For "
        "more info on CredSSP, see "
        "https://docs.microsoft.com/en-us/windows/desktop/secauthn/credential-security-support-provider"
    ),
}

supports_kerberos_cf = {
    "name": "supports_kerberos",
    "label": "Supports Kerberos",
    "type": "BOOL",
    "required": False,
    "description": (
        "If set to True, remote scripts will be run against this server using "
        "Kerberos, as opposed to NTLM or CredSSP. This setting also allows the "
        "credentials for this server to be trusted throughout the domain. "
        "See docs for required Kerberos configuraiton on the operating system."
    ),
}

gce_tags_cf = {
    "name": "gce_tags",
    "label": "GCE Network Tags",
    "type": "STR",
    "required": True,
    "show_on_servers": False,
    "description": (
        "A network tag name or comma-delimited list of network tag names that will be applied to a "
        "GCE VM during provisioning."
    ),
}

content_library_cf = {
    "name": "content_library",
    "label": "Content Library",
    "type": "TUP",
    "namespace": "vmware",
    "description": (
        "The Content Library associated with a VMware template. VMware Content Libraries allow admins"
        "to share VM templates across multiple vCenter instances.",
    ),
}

# Important! This cf field dict is copied in orders/migrations/0019_auto_20180119_1924.py.
# If changes are made, you'll need to change the migration.
annotation_cf = {
    "name": "annotation",
    "label": "Annotation",
    "type": "TXT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Notes that will be added to AWS or VMware hosts during provisioning. "
        "You may use parameterized templates in this field. "
        "Ex. 'Creator={{ server.owner }} Portal={{ portal.site_url }}'. For more "
        "info, see the docs on hostname templates."
    ),
}

nic_desc = (
    "Networks options are those available to the resource handler if they are "
    "also available to the group or environment"
)

nic1_cf = {
    "name": "sc_nic_0",
    "label": "NIC 1",
    "type": "NET",
    "required": True,
    "description": nic_desc,
}
nic2_cf = {"name": "sc_nic_1", "label": "NIC 2", "type": "NET", "description": nic_desc}
nic3_cf = {"name": "sc_nic_2", "label": "NIC 3", "type": "NET", "description": nic_desc}
nic4_cf = {"name": "sc_nic_3", "label": "NIC 4", "type": "NET", "description": nic_desc}
nic5_cf = {"name": "sc_nic_4", "label": "NIC 5", "type": "NET", "description": nic_desc}
nic6_cf = {"name": "sc_nic_5", "label": "NIC 6", "type": "NET", "description": nic_desc}
nic7_cf = {"name": "sc_nic_6", "label": "NIC 7", "type": "NET", "description": nic_desc}
nic8_cf = {"name": "sc_nic_7", "label": "NIC 8", "type": "NET", "description": nic_desc}
nic9_cf = {"name": "sc_nic_8", "label": "NIC 9", "type": "NET", "description": nic_desc}
nic10_cf = {
    "name": "sc_nic_9",
    "label": "NIC 10",
    "type": "NET",
    "description": nic_desc,
}

disk_1_size_cf = {
    "name": "disk_1_size",
    "label": "Size for Disk 2",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Size in GB of a second disk added to a server during provisioning "
        "(only supported on VMware, AWS, GCE, & Azure Resource Manager currently)"
    ),
}
disk_2_size_cf = {
    "name": "disk_2_size",
    "label": "Size for Disk 3",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Size in GB of a third disk added to a server during provisioning "
        "(only supported on VMware, AWS, GCE, & Azure Resource Manager currently)"
    ),
}
disk_3_size_cf = {
    "name": "disk_3_size",
    "label": "Size for Disk 4",
    "type": "INT",
    "required": False,
    "show_on_servers": False,
    "description": (
        "Size in GB of a fourth disk added to a server during provisioning "
        "(only supported on VMware, AWS, GCE, & Azure Resource Manager currently)"
    ),
}

open_ports_tcp_cf = {
    "name": "open_ports_tcp",
    "label": "Open TCP Ports",
    "type": "STR",
    "required": False,
    "show_on_servers": False,
    "description": (
        "TCP ports to open on a server. This can be a single integer or a range. "
        "Currently these are only applied to GCE and Azure Resource Manager servers. "
        "Examples: '22' or '5985-5986'"
    ),
}

open_ports_udp_cf = {
    "name": "open_ports_udp",
    "label": "Open UDP Ports",
    "type": "STR",
    "required": False,
    "show_on_servers": False,
    "description": (
        "UDP ports to open on a server. This can be a single integer or a range. "
        "Currently these are only applied to GCE and Azure Resource Manager servers. "
        "Examples: '22' or '5985-5986'"
    ),
}

os_services_cf = {
    "name": "os_services",
    "label": "OS Services",
    "type": "CODE",
    "required": False,
    "show_on_servers": False,
    "description": "JSON-serialized OS-specific services installed on a computer.",
}
os_users_cf = {
    "name": "os_users",
    "label": "OS Users",
    "type": "CODE",
    "required": False,
    "show_on_servers": False,
    "description": "JSON-serialized OS-specific users on a computer.",
}
os_disks_logical_cf = {
    "name": "os_disks_logical",
    "label": "OS Logical Disks",
    "type": "CODE",
    "required": False,
    "show_on_servers": False,
    "description": "JSON-serialized OS-specific logical disks on a computer.",
}
os_disks_physical_cf = {
    "name": "os_disks_physical",
    "label": "OS Physical Disks",
    "type": "CODE",
    "required": False,
    "show_on_servers": False,
    "description": "JSON-serialized OS-specific physical disks on a computer.",
}
os_partitions_cf = {
    "name": "os_partitions",
    "label": "OS Partitions",
    "type": "CODE",
    "required": False,
    "show_on_servers": False,
    "description": "JSON-serialized OS-specific partitions on a computer.",
}

# we create these at CB install time so that we can write code like
# "if svr.sc_nic_0_ip:" without having to worry about it throwing an
# AttributeError
# see https://cloudbolt.atlassian.net/browse/DEV-2596
nic1_ip_cf = {"name": "sc_nic_0_ip", "label": "NIC 1 IP", "type": "IP"}
nic2_ip_cf = {"name": "sc_nic_1_ip", "label": "NIC 2 IP", "type": "IP"}
nic3_ip_cf = {"name": "sc_nic_2_ip", "label": "NIC 3 IP", "type": "IP"}
nic4_ip_cf = {"name": "sc_nic_3_ip", "label": "NIC 4 IP", "type": "IP"}
nic5_ip_cf = {"name": "sc_nic_4_ip", "label": "NIC 5 IP", "type": "IP"}
nic6_ip_cf = {"name": "sc_nic_5_ip", "label": "NIC 6 IP", "type": "IP"}
nic7_ip_cf = {"name": "sc_nic_6_ip", "label": "NIC 7 IP", "type": "IP"}
nic8_ip_cf = {"name": "sc_nic_7_ip", "label": "NIC 8 IP", "type": "IP"}
nic9_ip_cf = {"name": "sc_nic_8_ip", "label": "NIC 9 IP", "type": "IP"}
nic10_ip_cf = {"name": "sc_nic_9_ip", "label": "NIC 10 IP", "type": "IP"}

server_cnt_cf = {
    "name": "server_cnt",
    "label": "Max. Servers Allowed Per Handler",
    "type": "INT",
}
quantity_cf = dict(
    name="quantity",
    label="Quantity",
    description="Number of servers to build",
    type="INT",
    required=False,
    show_on_servers=False,
    global_constraints={"minimum": 0},
)

skip_network_config_cf = {
    "name": "c2_skip_network_conf",
    "label": "Skip Network Configuration",
    "type": "BOOL",
}

skip_rh_hostname_validation_cf = {
    "name": "skip_rh_hostname_validation",
    "label": "Skip RH Hostname Validation",
    "description": "If set to True, the provisioning job will skip calling the resource handler "
    "to check whether the VM name is already in use. This can speed up "
    "provisioning, but may lead to job failures due to name collisions.",
    "type": "BOOL",
}

nsx_scope_cf = {
    "name": "nsx_scope",
    "label": "NSX Transport Zone",
    "type": "NSXS",
    "namespace": "advanced_networking",
}
nsx_edge_cf = {
    "name": "nsx_edge",
    "label": "NSX Edge",
    "type": "NSXE",
    "namespace": "advanced_networking",
}
nsxt_tz_cf = {
    "name": "nsxt_transport_zone",
    "label": "NSXT Transport Zone",
    "type": "STR",
    "namespace": "advanced_networking",
}
nsxt_tier0_cf = {
    "name": "nsxt_tier_0",
    "label": "NSXT Tier 0",
    "type": "STR",
    "namespace": "advanced_networking",
}
nsxt_tier1_cf = {
    "name": "nsxt_tier_1",
    "label": "NSXT Tier 1",
    "type": "STR",
    "namespace": "advanced_networking",
}

key_name_cf = {
    "name": "key_name",
    "label": "Key pair name",
    "type": "STR",
    "required": True,
    "description": (
        "Name of an SSH Key that is referenceable in CloudBolt.  Keys can be used to "
        "access resources or run remote scripts where applicable."
    ),
}

server_lock_cf = {
    "name": "server_lock",
    "label": "Server Lock",
    "type": "STR",
    "description": (
        "Locks a server to prevent the specified action. "
        "Remove the parameter from the server to unlock it."
    ),
    "required": False,
    "show_on_servers": True,
    "available_all_servers": True,
}

nla_for_rdp_cf = {
    "name": "nla_for_rdp",
    "label": "Use NLA for RDP",
    "type": "BOOL",
    "description": (
        "Use Network Level Authentication when accessing a "
        "server with Remote Desktop."
    ),
    "show_on_servers": True,
}

license_type_cf = {
    "name": "license_type",
    "label": "Azure License Type",
    "type": "STR",
    "description": (
        "Used with Azure to indicate the use of a "
        "particular license type when provisioning. "
        "For example, can be used for BYOL by giving "
        'a value of "Windows_Server".'
    ),
}

skip_security_group_cf = {
    "name": "skip_security_group",
    "label": "Skip Security Group Creation",
    "type": "BOOL",
    "description": (
        "If set to true, the Azure server will not receive "
        "its own network security group. The subnet security "
        "group will still apply."
    ),
}

power_schedule_cf = {
    "name": "power_schedule",
    "label": "Power Schedule",
    "type": "STR",
    "description": (
        "Used to set the power control schedule for a server at order "
        "time. Not visible on the server after provisioning, because "
        "it is transformed into a power schedule during provisioning."
    ),
}

vmware_sysprep_file_cf = {
    "name": "vmware_sysprep_file",
    "label": "Sysprep Answer File",
    "type": "CODE",
    "required": True,
    "description": (
        "A Sysprep answer file that is used to customize a Windows "
        "VMware template during the OS customization process when "
        "provisioning servers using the vCenter Resource Handler."
    ),
}

created_by_terraform_cf = {
    "name": "created_by_terraform",
    "type": "BOOL",
    "label": "Created By Terraform",
    "show_on_servers": True,
    "description": "Used as a way to identify servers that were created from "
    "Terraform Plans within CloudBolt.",
}

resource_handler_cf = {
    "name": "resource_handler",
    "type": "STR",
    "label": "Resource Handler",
    "show_on_servers": True,
    "description": "The owning Resource Handler.",
}

dataprotection_plan_cf = {
    "name": "dataprotection_plan",
    "label": "Data Protection Plan",
    "type": "STR",
    "show_on_servers": True,
    "show_as_attribute": True,
    "description": (
        "Used to add VMs to protection plans provided by data "
        "protection backend systems."
    ),
    "allow_multiple": False,
}

use_private_key_for_ssh_sessions_cf = {
    "name": "use_private_key_for_ssh_sessions",
    "type": "BOOL",
    "label": "Use private key for SSH sessions",
    "show_on_servers": True,
    "available_all_servers": True,
    "description": "True if SSH sessions should prompt for a private key file. "
    "False if SSH sessions should use username and password instead.",
}

all_hw_cfs = [mem_size_cf, cpu_cnt_cf, disk_size_cf]
all_network_cfs = [
    nic1_cf,
    nic2_cf,
    nic3_cf,
    nic4_cf,
    nic5_cf,
    nic6_cf,
    nic7_cf,
    nic8_cf,
    nic9_cf,
    nic10_cf,
    nic1_ip_cf,
    nic2_ip_cf,
    nic3_ip_cf,
    nic4_ip_cf,
    nic5_ip_cf,
    nic6_ip_cf,
    nic7_ip_cf,
    nic8_ip_cf,
    nic9_ip_cf,
    nic10_ip_cf,
]

all_cfs = (
    all_hw_cfs
    + all_network_cfs
    + [
        expiration_date_cf,
        vm_pool_cf,
        time_zone_cf,
        username_cf,
        password_cf,
        new_password_cf,
        domain_cf,
        dns_domain_cf,
        domain_name_server_cf,
        server_cnt_cf,
        os_license_key_cf,
        vmware_datastore_cf,
        vmware_datastore_minimum_freespace_cf,
        vmware_disk_controller_cf,
        vmware_disk_controller_label_cf,
        vmware_cluster_cf,
        vmware_dns_search_path,
        skip_network_config_cf,
        skip_rh_hostname_validation_cf,
        chef_environment_cf,
        ansible_run_timeout,
        new_disk_size_cf,
        vmware_disk_type_cf,
        extend_root_disk_cf,
        vm_customization_timeout_cf,
        post_prov_delay_cf,
        link_clone_cf,
        disk_1_size_cf,
        disk_2_size_cf,
        disk_3_size_cf,
        hostname_template_cf,
        tech_specific_script_execution_cf,
        annotation_cf,
        quantity_cf,
        nsx_scope_cf,
        nsx_edge_cf,
        nsxt_tz_cf,
        nsxt_tier0_cf,
        nsxt_tier1_cf,
        key_name_cf,
        server_lock_cf,
        nla_for_rdp_cf,
        open_ports_tcp_cf,
        open_ports_udp_cf,
        os_services_cf,
        os_users_cf,
        supports_credssp_cf,
        supports_kerberos_cf,
        os_disks_logical_cf,
        os_disks_physical_cf,
        os_partitions_cf,
        license_type_cf,
        skip_security_group_cf,
        power_schedule_cf,
        gce_tags_cf,
        vmware_sysprep_file_cf,
        content_library_cf,
        created_by_terraform_cf,
        dataprotection_plan_cf,
        use_private_key_for_ssh_sessions_cf,
    ]
)

# FIELD DEPENDENCIES ###
field_dependencies = []

# GLOBAL OPTIONS FOR CFs ###
all_cfos = {}

# Add AWS cfs and field dependencies if there is at least one AWSHandler
if AWSHandler.objects.count():
    from resourcehandlers.aws.aws_minimal import aws_cfs, aws_field_dependencies

    all_cfs.extend(aws_cfs)
    field_dependencies.extend(aws_field_dependencies)

# Add SoftLayer cfs if there is at least one SlayerResourceHandler
if SlayerResourceHandler.objects.count():
    from resourcehandlers.slayer.slayer_minimal import slayer_cfs

    all_cfs.extend(slayer_cfs)

# Add Hyper-V cfs if there is at least one HyperVResourceHandler
if HyperVResourceHandler.objects.count():
    from resourcehandlers.hyperv.constants import hyperv_cfs

    all_cfs.extend(hyperv_cfs)

# Add SCVMM cfs if there is at least one HyperVResourceHandler
if SCVMMHandler.objects.count():
    from resourcehandlers.scvmm.scvmm_minimal import scvmm_cfs

    all_cfs.extend(scvmm_cfs)

# Add Libcloud cfs if there is at least one LibcloudHandler subclass
if GCEHandler.objects.exists() or OpenStackHandler.objects.exists():
    from resourcehandlers.libcloudhandler.libcloud_minimal import libcloud_cfs

    all_cfs.extend(libcloud_cfs)

# Add GCP cfs if there is at least one GCPHandler
if GCPHandler.objects.count():
    from resourcehandlers.gcp.gcp_minimal import gcp_cfs

    all_cfs.extend(gcp_cfs)

# Add OpenStack cfs if there is at least one OpenStackHandler (or HelionHandler)
if OpenStackHandler.objects.exists() or HelionHandler.objects.exists():
    from resourcehandlers.openstack.openstack_minimal import os_cfs

    all_cfs.extend(os_cfs)

# Add Azure Resource Manager cfs and field dependencies if there is at least one AzureARMHandler
if AzureARMHandler.objects.count():
    from resourcehandlers.azure_arm.azure_minimal import (
        azure_cfs,
        azure_cfos,
        arm_field_dependencies,
    )

    all_cfs.extend(azure_cfs)
    field_dependencies.extend(arm_field_dependencies)
    all_cfos.update(azure_cfos)

# Add GCE cfs if there is at least one GCEHandler
if GCEHandler.objects.count():
    from resourcehandlers.gce.gce_minimal import gce_cfs

    all_cfs.extend(gce_cfs)

# Add vCloud Director cfs if there is at least one VCDHandler
if VCDHandler.objects.count():
    from resourcehandlers.vcloud_director.vcd_minimal import vcd_cfs

    all_cfs.extend(vcd_cfs)

# Add Nutanix cfs if there is at least one AcropolisResourceHandler
if AcropolisResourceHandler.objects.count():
    from resourcehandlers.acropolis.acropolis_minimal import acropolis_cfs

    all_cfs.extend(acropolis_cfs)

# Add Alibaba cfs, dependencies, etc. if there is at least one AlibabaResourceHandler
if AlibabaResourceHandler.objects.count():
    from resourcehandlers.alibaba.alibaba_minimal import (
        alibaba_cfs,
        alibaba_field_dependencies,
    )

    all_cfs.extend(alibaba_cfs)
    field_dependencies.extend(alibaba_field_dependencies)

# Add OCI cfs if there is at least one OCIResourceHandler
if OCIResourceHandler.objects.count():
    from resourcehandlers.oci.oci_minimal import oci_cfs

    all_cfs.extend(oci_cfs)

# Add Outscale cfs if there is at least one OutscaleResourceHandler
if OutscaleResourceHandler.objects.count():
    from resourcehandlers.outscale.outscale_minimal import outscale_cfs

    all_cfs.extend(outscale_cfs)

# Add Maas cfs if there is at least one MaasResourceHandler
if MaasResourceHandler.objects.count():
    from resourcehandlers.maas.maas_minimal import maas_cfs

    all_cfs.extend(maas_cfs)

# CUSTOM FIELDS ###

# CUSTOM FIELD VALUES ###
all_cfvs = {}
all_cfvs["vmware_disk_type"] = []
for disk_type, disk_type_display in VmwareDisk.PROV_TYPE_CHOICES:
    all_cfvs["vmware_disk_type"].append(disk_type_display)

# PRECONFIGURATIONS & OPTIONS ###
vm_size_small = {}
vm_size_small["name"] = "small"
vm_size_small["values"] = {"mem_size": "1", "cpu_cnt": "1"}

vm_size_medium = {}
vm_size_medium["name"] = "medium"
vm_size_medium["values"] = {"mem_size": "4", "cpu_cnt": "2"}

vm_size_large = {}
vm_size_large["name"] = "large"
vm_size_large["values"] = {"mem_size": "8", "cpu_cnt": "4"}

vm_size_preconfig = {}
vm_size_preconfig["name"] = "vm_size"
vm_size_preconfig["label"] = "Server Size"
vm_size_preconfig["options"] = [vm_size_small, vm_size_medium, vm_size_large]

all_preconfigs = [vm_size_preconfig]

# TECHNOLOGIES ###
aws_restech = {}
aws_restech["name"] = "Amazon Web Services"
aws_restech["module"] = "resourcehandlers.aws.aws_wrapper"
aws_restech["slug"] = "aws"
aws_restech["version"] = ""

aws_govcloud_restech = {}
aws_govcloud_restech["name"] = "AWS GovCloud (US)"
aws_govcloud_restech["module"] = "resourcehandlers.aws.aws_wrapper"
aws_govcloud_restech["slug"] = "aws_govcloud"
aws_govcloud_restech["version"] = ""

aws_china_restech = {}
aws_china_restech["name"] = " AWS China - 亚马逊"
aws_china_restech["module"] = "resourcehandlers.aws.aws_wrapper"
aws_china_restech["slug"] = "aws_china"
aws_china_restech["version"] = ""

vsphere_restech = {}
vsphere_restech["name"] = "VMware vCenter"
vsphere_restech["version"] = "4.1/5.x"
vsphere_restech["module"] = "resourcehandlers.vmware.vmware_41"

xen_restech = {}
xen_restech["name"] = "Xen"
xen_restech["version"] = "1.0"
xen_restech["module"] = "resourcehandlers.xen.ase_xenapi_common"

qemu_restech = {}
qemu_restech["name"] = "QEMU-KVM"
qemu_restech["version"] = "1.2"
qemu_restech["module"] = "resourcehandlers.qemu.qemu-kvm"

ipmi_restech = {}
ipmi_restech["name"] = "IPMI"
ipmi_restech["version"] = ""
ipmi_restech["module"] = "resourcehandlers.ipmi.ipmitool_1_8_11"

slayer_restech = {}
slayer_restech["name"] = "IBM Cloud"
slayer_restech["version"] = "1.0"
slayer_restech["slug"] = "ibm_cloud"
slayer_restech["module"] = "resourcehandlers.slayer.cb_slayerapi_common"

ibm_gov_restech = {}
ibm_gov_restech["name"] = "IBM Cloud for Government"
ibm_gov_restech["version"] = "1.0"
ibm_gov_restech["slug"] = "ibm_gov"
ibm_gov_restech["module"] = "resourcehandlers.slayer.cb_slayerapi_common"

hyperv_restech = {}
hyperv_restech["name"] = "Hyper-V"
hyperv_restech["version"] = "1.0"
hyperv_restech["module"] = "resourcehandlers.hyperv.hyperv_wrapper"

acropolis_restech = {}
acropolis_restech["name"] = "Nutanix Acropolis"
acropolis_restech["version"] = "1.0"
acropolis_restech["module"] = "resourcehandlers.acropolis.acropolis_wrapper"

gce_restech = {}
gce_restech["name"] = "Google Compute Engine"
gce_restech["version"] = ""
gce_restech["module"] = "resourcehandlers.gce.gce_wrapper"

gcp_restech = {}
gcp_restech["name"] = "Google Cloud Platform"
gcp_restech["version"] = ""
gcp_restech["slug"] = "gcp"
gcp_restech["module"] = "resourcehandlers.gcp.gcp_wrapper"

os_restech = {}
os_restech["name"] = "OpenStack"
os_restech["version"] = ""
os_restech["module"] = "resourcehandlers.openstack.openstack_wrapper"

helion_restech = {}
helion_restech["name"] = "HP Helion"
helion_restech["version"] = ""
helion_restech["module"] = "resourcehandlers.helion.helion_wrapper"

azure_arm_restech = {}
azure_arm_restech["name"] = "Azure"
azure_arm_restech["version"] = ""
azure_arm_restech["module"] = "resourcehandlers.azure_arm.azure_wrapper"

azure_stack_restech = {}
azure_stack_restech["name"] = "Azure Stack"
azure_stack_restech["version"] = ""
azure_stack_restech["module"] = "resourcehandlers.azure_stack.azure_wrapper"

oci_restech = {}
oci_restech["name"] = "Oracle Cloud Infrastructure"
oci_restech["version"] = "1.0"
oci_restech["module"] = "resourcehandlers.oci.oci_wrapper"

outscale_restech = {}
outscale_restech["name"] = "Outscale"
outscale_restech["version"] = ""
outscale_restech["module"] = "resourcehandlers.outscale.outscale_wrapper"

maas_restech = {}
maas_restech["name"] = "MAAS"
maas_restech["version"] = "1.0"
maas_restech["module"] = "resourcehandlers.maas.maas_wrapper"

razor_provtech = {}
razor_provtech["name"] = "Razor"
razor_provtech["version"] = "1"

hp10_orchtech = {}
hp10_orchtech["name"] = "HP Operations Orchestration"
hp10_orchtech["version"] = "10"
hp10_orchtech["modulename"] = "orchestrationengines.hpoo.hpoo_10_api"

hp9_orchtech = {}
hp9_orchtech["name"] = "HP Operations Orchestration"
hp9_orchtech["version"] = "9.x"
hp9_orchtech["modulename"] = "orchestrationengines.hpoo.hpoo_9_api"

vc_orchtech = {}
vc_orchtech["name"] = "vCenter/vRealize Orchestrator"
vc_orchtech["version"] = "5.5 - 7.0.1+"
vc_orchtech["modulename"] = "orchestrationengines.vco.vco_api"

alibaba_restech = {}
alibaba_restech["name"] = "Alibaba Cloud"
alibaba_restech["version"] = ""
alibaba_restech["module"] = "resourcehandlers.alibaba.alibaba_wrapper"

kube_tech = {"name": "Kubernetes"}

infoblox_ipamtech = {}
infoblox_ipamtech["name"] = "Infoblox"
infoblox_ipamtech["version"] = ""
infoblox_ipamtech["modulename"] = "ipam.infoblox.infoblox_wrapper"

phpipam_ipamtech = {}
phpipam_ipamtech["name"] = "phpIPAM"
phpipam_ipamtech["version"] = ""
phpipam_ipamtech["modulename"] = "ipam.phpipam.phpipam_wrapper"

bluecat_ipamtech = {}
bluecat_ipamtech["name"] = "BlueCat"
bluecat_ipamtech["version"] = ""
bluecat_ipamtech["modulename"] = "ipam.bluecat.bluecat_wrapper"

solarwinds_ipamtech = {}
solarwinds_ipamtech["name"] = "SolarWinds"
solarwinds_ipamtech["version"] = ""
solarwinds_ipamtech["modulename"] = "ipam.solarwindsipam.solarwindsipam_wrapper"

servicenow_itsmtech = {}
servicenow_itsmtech["name"] = "ServiceNow"
servicenow_itsmtech["version"] = ""
servicenow_itsmtech["modulename"] = "itsm.servicenow.wrapper"

nsxt_network_virtualization_tech = {}
nsxt_network_virtualization_tech["name"] = "NSX-T"
nsxt_network_virtualization_tech["version"] = ""
nsxt_network_virtualization_tech[
    "modulename"
] = "network_virtualization.nsx_t.nsxt_wrapper"

vmc_aws = {}
vmc_aws["name"] = "VMware Cloud on AWS"
vmc_aws["version"] = ""
vmc_aws["module"] = "resourcehandlers.vmware_cloud_aws.vmc_wrapper"
vmc_aws["slug"] = "vmc_aws"

scvmm_restech = {}
scvmm_restech["name"] = "SCVMM"
scvmm_restech["version"] = ""
scvmm_restech["module"] = "resourcehandlers.scvmm.scvmm_wrapper"
scvmm_restech["slug"] = "scvmm"

all_resource_technologies = [
    vsphere_restech,
    xen_restech,
    qemu_restech,
    aws_restech,
    aws_govcloud_restech,
    aws_china_restech,
    ipmi_restech,
    gce_restech,
    gcp_restech,
    os_restech,
    azure_arm_restech,
    azure_stack_restech,
    helion_restech,
    slayer_restech,
    ibm_gov_restech,
    hyperv_restech,
    acropolis_restech,
    alibaba_restech,
    oci_restech,
    outscale_restech,
    vmc_aws,
    scvmm_restech,
    maas_restech,
]
all_prov_technologies = [razor_provtech]
all_orchestration_technologies = [hp10_orchtech, hp9_orchtech, vc_orchtech]
all_container_technologies = [kube_tech]
all_ipam_technologies = [
    infoblox_ipamtech,
    phpipam_ipamtech,
    bluecat_ipamtech,
    solarwinds_ipamtech,
]
all_itsm_technologies = [
    servicenow_itsmtech,
]
all_network_virtualization_technologies = [nsxt_network_virtualization_tech]

all_load_balancer_technologies = [
    {"name": "F5 Big-IP", "type_slug": "f5"},
    {"name": "AWS ELB", "type_slug": "aws_elb"},
    {"name": "HA Proxy", "type_slug": "haproxy"},
    {"name": "NSX ESG", "type_slug": "nsx_esg"},
    {"name": "Azure ALB", "type_slug": "azure_alb"},
]

# END TECHNOLOGIES ###

# ENVIRONMENTS ###
# name and resource_handler are required to be set for each user defined
# environment every CB instance will have a single 'UNASSIGNED' Environment
# for discovered servers
# provision_engine is optional for environments that support template built OS
# osbuilds, software_policies, preconfig_info, and resource_pool are optional

environment0 = {}
environment0["name"] = "Unassigned"

all_environments = [environment0]
# END ENVIRONMENTS ###


# GROUPS ###
unassigned_group = {"name": "Unassigned", "type": "Organization", "parent": None}
all_groups = [unassigned_group]
# END GROUPS ###

# PERMISSIONS ###
all_permissions = [
    {
        "name": "order.approve",
        "label": "Approve Orders",
        "description": "Allows the user to approve and deny orders",
    },
    {"name": "order.view", "label": "View Orders", "description": ""},
    {
        "name": "order.submit",
        "label": "Submit Orders",
        "description": "Allows the user to order servers and blueprints",
    },
    {
        "name": "order.change_attributes",
        "label": "Change Order Attributes",
        "description": "Change the order name",
    },
    {
        "name": "order.choose_recipient",
        "label": "Choose Recipient for Orders",
        "description": "Allows the user to choose a recipient other than "
        "themself to own the Server(s) and/or Resource(s) created by an order",
    },
    {"name": "server.view", "label": "View Servers", "description": ""},
    {
        "name": "server.control_power",
        "label": "Control Power on Servers",
        "description": "Power on, power off, reboot, and pause servers",
    },
    {
        "name": "server.manage_snapshots",
        "label": "Manage Snapshots",
        "description": "Create, delete, and restore from server snapshots",
    },
    {
        "name": "server.add_disks",
        "label": "Add Disks",
        "description": "Allows the user to add disks to a server",
    },
    {
        "name": "server.remove_disks",
        "label": "Remove Disks",
        "description": "Allows the user to remove disks from a server",
    },
    {
        "name": "server.resize_disks",
        "label": "Resize Disks",
        "description": "Allows the user to resize disks on a server",
    },
    {"name": "server.manage_nics", "label": "Manage NICs", "description": ""},
    {
        "name": "server.change_resources",
        "label": "Change Resources",
        "description": "Change CPU & memory on VMs",
    },
    {
        "name": "server.resize",
        "label": "Resize VM",
        "description": "Change the type (size) of this Virtual Machine",
    },
    {"name": "server.console", "label": "Console", "description": ""},
    {
        "name": "server.remote_terminal",
        "label": "Remote Terminal",
        "description": "SSH/RDP access to servers from the CloudBolt UI",
    },
    {
        "name": "server.manage_applications",
        "label": "Manage Apps",
        "description": "[Un]Install config manager applications on servers",
    },
    {
        "name": "server.change_attributes",
        "label": "Change Attributes",
        "description": "Change env, group, OS family, and OS build associates for servers",
    },
    {
        "name": "server.manage_labels",
        "label": "Manage Labels",
        "description": "Add and remove labels on servers",
    },
    {
        "name": "server.manage_parameters",
        "label": "Manage Server Parameters",
        "description": "Add, remove, and modify parameters (AKA custom fields) on servers",
    },
    {"name": "server.delete", "label": "Delete Server", "description": ""},
    {
        "name": "server.manage_credentials",
        "label": "Manage Server Credentials",
        "description": "Allows the user to view and manage the credentials used "
        "to execute remote actions on servers.",
    },
    {
        "name": "server.view_handler_specific_details",
        "label": "View Handler-Specific Details",
        "description": "Allows the user to see resource handler specific details "
        "for servers. Ex. The VMware cluster, the AWS region, etc.",
    },
    {
        "name": "server.all_actions",
        "label": "Run All Server Actions",
        "description": "Allows the user to execute any Server Action available "
        "on the server",
    },
    {
        "name": "server.view_power_schedule",
        "label": "View Server's Power Schedule",
        "description": "Allows the user the see the schedule for recurring "
        "power control on the server",
    },
    {
        "name": "server.manage_power_schedule",
        "label": "Manage Server's Power Schedule",
        "description": "Allows the user the edit the schedule for recurring "
        "power control on the server",
    },
    {"name": "resource.view", "label": "View Resources", "description": ""},
    {
        "name": "resource.change_attributes",
        "label": "Change Resource Attributes",
        "description": "",
    },
    {
        "name": "resource.manage_parameters",
        "label": "Manage Resource Parameters",
        "description": "Add, remove, and modify parameters (AKA custom fields) on resources",
    },
    {
        "name": "resource.view_power_schedule",
        "label": "View Resource's Power Schedule",
        "description": "Allows the user the see the schedule for recurring "
        "power control on the resource",
    },
    {
        "name": "resource.manage_power_schedule",
        "label": "Manage Resource's Power Schedule",
        "description": "Allows the user the edit the schedule for recurring "
        "power control on the resource",
    },
    {
        "name": "resource.all_actions",
        "label": "Run All Resource Actions",
        "description": "Allows the user to execute any Resource Action available "
        "on the resource",
    },
    {"name": "group.view", "label": "View Group Details", "description": ""},
    {
        "name": "group.change_attributes",
        "label": "Change Group Attributes",
        "description": "",
    },
    {"name": "group.delete", "label": "Delete Group", "description": ""},
    {"name": "group.create_subgroup", "label": "Create Subgroup", "description": ""},
    {
        "name": "group.manage_members",
        "label": "Manage Group Memberships",
        "description": "",
    },
    {
        "name": "group.manage_members_view_unassigned_users",
        "label": "Manage Group Memberships - View Unassigned Users",
        "description": (
            "Allows the user to view and add users to groups they manage that do not "
            "currently have a group assigned to them (such as new users). Requires "
            "group.manage_members permission to apply"
        ),
    },
    {
        "name": "group.manage_networks",
        "label": "Manage Group Networks",
        "description": "",
    },
    {
        "name": "group.manage_parameters",
        "label": "Manage Group Parameters",
        "description": "",
    },
    {
        "name": "group.manage_subgroup_quotas",
        "label": "Manage Subgroup Quotas",
        "description": "Allows the user to manage quotas for subgroups of this group",
    },
    {
        "name": "blueprint.manage",
        "label": "Manage Blueprints",
        "description": (
            "Allows the user to perform most management actions on Blueprints that "
            "the Group can manage, such as setting the Resource Type, allowing additional "
            "Groups to manage or deploy it, adding Build Items, and many more. "
            "Exceptions that are instead provided by other specific permissions include "
            "the ability to configure the Blueprint so any Group can deploy it and "
            "create a new Parameter from the Blueprint"
        ),
    },
    {
        "name": "blueprint.create_parameters",
        "label": "Create Blueprint Parameters",
        "description": "Allows the user to create just Blueprint Parameters",
    },
    # NOTE: from this point forward, no new CB instance will have this permission in
    # any Role OOTB. However, to avoid unpleasant surprises for existing customers,
    # it will be added to any existing Role with blueprint.manage on rollout
    {
        "name": "blueprint.any_group_can_deploy",
        "label": "Configure Blueprints so Any Group Can Deploy",
        "description": (
            "Allows the user to modify the setting on a Blueprint that makes it "
            "available to be deployed by any and all Groups on the instance, both "
            "current and future. Exercise caution with this permission, since "
            "it can have a broad impact"
        ),
    },
    {"name": "job.view", "label": "View Jobs", "description": ""},
    {
        "name": "job.view_logs",
        "label": "View Job Logs",
        "description": "Allows the user to view and download job logs.",
    },
    {
        "name": "job.cancel",
        "label": "Cancel Jobs",
        "description": "Allows the user to cancel jobs in progress.",
    },
    {
        "name": "job.rerun",
        "label": "Re-run Jobs",
        "description": "Allows the user to re-run failed jobs.",
    },
    {
        "name": "dataprotection.manage_parameter_dataprotection_plan",
        "label": "Manage Data Protection Plan",
        "description": "Allows the user to manage servers' data protection plans.",
    },
    {
        "name": "dataprotection.restore_from_snapshot",
        "label": "Restore Data Protection Snapshots",
        "description": "Allows the user to restore a host from a Data Protection snapshot.",
    },
]
# END PERMISSIONS ###

# SPECIAL ROLES ###
# Permissions for the roles below will only be added when the role is created.
# create_objects will respect the existing permissions on upgrade.
# To add a new permission, add it here for CB configurations that
# don't yet have the role, then add a data migration to add it to
# existing roles.
all_special_roles = [
    {
        "name": "server_owner",
        "label": "Server Owner",
        "description": "Permissions that are granted to owners of servers",
        "assignable_to_users": False,
        "permissions": [
            "server.view",
            "server.control_power",
            "server.manage_snapshots",
            "server.add_disks",
            "server.remove_disks",
            "server.resize_disks",
            "server.manage_nics",
            "server.change_resources",
            "server.console",
            "server.remote_terminal",
            "server.manage_applications",
            "server.change_attributes",
            "server.manage_labels",
            "server.manage_parameters",
            "server.delete",
            "server.manage_credentials",
            "server.view_handler_specific_details",
            "server.all_actions",
            "server.view_power_schedule",
            "server.manage_power_schedule",
        ],
    },
    {
        "name": "resource_owner",
        "label": "Resource Owner",
        "description": "Permissions that are granted to owners of resources",
        "assignable_to_users": False,
        "permissions": [
            "resource.view",
            "resource.change_attributes",
            "resource.manage_parameters",
            "resource.all_actions",
            "resource.view_power_schedule",
            "resource.manage_power_schedule",
        ],
    },
    {
        "name": "job_owner",
        "label": "Job Owner",
        "description": "Permissions that are granted to owners of jobs",
        "assignable_to_users": False,
        "permissions": ["job.view", "job.view_logs", "job.rerun", "job.cancel"],
    },
]
# END SPECIAL ROLES ###

# DEFAULT ROLES ###
# These roles are not created by create_objects; instead, the original set was created by
# the 0011_migrate_existing_roles.py migration in accounts. This list is used
# for restoring the default initial roles via the UI.
# If you need to change any of these roles, add a data migration to change it
# during the upgrader/installer, then add the change here for when the role is
# restored via the UI. Likewise, you will also need a data migration to add a new role.
# One reason to use the data migration approach is to avoid re-creating these roles if a
# customer has deleted them.
all_default_roles = [
    {
        "name": "requestor",
        "label": "Requestor",
        "description": "May submit provisioning, modification, and decommissioning "
        "orders in this group",
        "assignable_to_users": True,
        "permissions": ["order.submit"],
    },
    {
        "name": "viewer",
        "label": "Viewer",
        "description": "Basic permission to view group servers, members, and "
        "activity",
        "assignable_to_users": True,
        "permissions": [
            "order.view",
            "server.view",
            "server.view_power_schedule",
            "resource.view",
            "resource.view_power_schedule",
            "group.view",
        ],
    },
    {
        "name": "approver",
        "label": "Approver",
        "description": "May approve or deny orders for this group",
        "assignable_to_users": True,
        "permissions": ["order.view", "order.change_attributes", "order.approve"],
    },
    {
        "name": "resource_admin",
        "label": "Resource Admin",
        "description": "Manages technical configuration for this group, "
        "such as parameters and networks. Can also manage "
        "blueprints and servers.",
        "assignable_to_users": True,
        "permissions": [
            "order.submit",
            "server.view",
            "server.control_power",
            "server.manage_snapshots",
            "server.add_disks",
            "server.remove_disks",
            "server.resize_disks",
            "server.manage_nics",
            "server.change_resources",
            "server.console",
            "server.remote_terminal",
            "server.manage_applications",
            "server.change_attributes",
            "server.manage_labels",
            "server.manage_parameters",
            "server.delete",
            "server.manage_credentials",
            "server.view_handler_specific_details",
            "server.view_power_schedule",
            "server.manage_power_schedule",
            "resource.view",
            "resource.change_attributes",
            "resource.manage_parameters",
            "resource.view_power_schedule",
            "resource.manage_power_schedule",
            "blueprint.manage",
            "group.view",
            "group.change_attributes",
            "group.manage_networks",
            "group.manage_parameters",
        ],
    },
    {
        "name": "group_admin",
        "label": "Group Admin",
        "description": "Manages organizational aspects of this group: "
        "membership and permissions, subgroup creation and "
        "management, and delegation of responsibilities to "
        "other group members",
        "assignable_to_users": True,
        "permissions": [
            "group.view",
            "group.change_attributes",
            "group.create_subgroup",
            "group.delete",
            "group.manage_members",
            "group.manage_subgroup_quotas",
        ],
    },
    {
        "name": "delegate_server_owner",
        "label": "Delegate Server Owner",
        "description": (
            "Can be assigned to Users in a Server's management Groups, "
            "in order to provide additional Users with permissions "
            "comparable to the Owner of that Server."
        ),
        "assignable_to_users": True,
        "permissions": [
            "server.view",
            "server.control_power",
            "server.manage_snapshots",
            "server.add_disks",
            "server.remove_disks",
            "server.resize_disks",
            "server.manage_nics",
            "server.change_resources",
            "server.console",
            "server.remote_terminal",
            "server.manage_applications",
            "server.change_attributes",
            "server.manage_labels",
            "server.manage_parameters",
            "server.delete",
            "server.manage_credentials",
            "server.view_handler_specific_details",
            "server.all_actions",
            "server.view_power_schedule",
            "server.manage_power_schedule",
        ],
    },
]
# END DEFAULT ROLES ###

# GROUPTYPE ROLES ###
# These roles are listed separately from the default list above partially so they
# can be created by create_objects and partially because they need a relationship
# to one or more GroupTypes, which will be created if they don't exist yet
all_grouptype_roles = [
    {
        "name": "reassigner",
        "label": "Reassigner",
        "description": "May change attributes on Servers and Resources in order to "
        "reassign them to different Groups, Environments, and Owners as needed",
        "assignable_to_users": True,
        "permissions": [
            "server.view",
            "server.change_attributes",
            "resource.view",
            "resource.change_attributes",
        ],
        "group_types": ["Discovered Resources"],
    },
]
# END GROUPTYPE ROLES ###

# OS FAMILIES ###
# make sure children are listed *after* their parents
os_families = [
    {
        "name": "Linux",
        "parent": None,
        "inline_icon": "initialize/osfamily-icons/linux-16.png",
        "display_icon": "initialize/osfamily-icons/linux-128.png",
    },
    # Important! windows is re-created in orders/migrations/0019_auto_20180119_1924.py
    # any changes here should also be made there, and vice versa.
    {
        "name": "Windows",
        "parent": None,
        "inline_icon": "initialize/osfamily-icons/windows-16.png",
        "display_icon": "initialize/osfamily-icons/windows-128.png",
    },
    {
        "name": "Unix",
        "parent": None,
        "inline_icon": "initialize/osfamily-icons/unix-16.png",
        "display_icon": "initialize/osfamily-icons/unix-128.png",
    },
    {
        "name": "Red Hat",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/redhat-16.png",
        "display_icon": "initialize/osfamily-icons/redhat-128.png",
    },
    {
        "name": "Fedora",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/fedora-16.png",
        "display_icon": "initialize/osfamily-icons/fedora-128.png",
    },
    {
        "name": "Ubuntu",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/ubuntu-16.png",
        "display_icon": "initialize/osfamily-icons/ubuntu-128.png",
    },
    {
        "name": "CentOS",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/centos-16.png",
        "display_icon": "initialize/osfamily-icons/centos-128.png",
    },
    {
        "name": "CoreOS",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/coreos-16.png",
        "display_icon": "initialize/osfamily-icons/coreos-128.png",
    },
    {
        "name": "Oracle Enterprise Linux",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/oel-16.png",
        "display_icon": "initialize/osfamily-icons/oel-128.png",
    },
    {
        "name": "ESXi",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/esxi-16.png",
        "display_icon": "initialize/osfamily-icons/esxi-128.png",
    },
    {
        "name": "SUSE",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/suse-16.png",
        "display_icon": "initialize/osfamily-icons/suse-128.png",
    },  # add debian icon
    {
        "name": "Debian",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/debian.png",
        "display_icon": "initialize/osfamily-icons/debian.png",
    },
    {
        "name": "Amazon Linux",
        "parent": "Linux",
        "inline_icon": "initialize/osfamily-icons/amazon_linux-16.png",
        "display_icon": "initialize/osfamily-icons/amazon_linux-128.png",
    },
    {
        "name": "macOS",
        "parent": "Unix",
        "inline_icon": "initialize/osfamily-icons/macos-16.png",
        "display_icon": "initialize/osfamily-icons/macos-128.png",
    },
    {
        "name": "Solaris",
        "parent": "Unix",
        "inline_icon": "initialize/osfamily-icons/solaris-16.png",
        "display_icon": "initialize/osfamily-icons/solaris-128.png",
    },
]
# END OS FAMILIES ###

# HOOK-RELATED OBJECTS ###
hook_points = [
    {
        "name": "pre_syncvms",
        "label": "Pre Sync VMs",
        "description": (
            "Executes at the beginning of a Sync VMs " "from Resource Handlers job."
        ),
        "job_type": "syncvms",
    },
    {
        "name": "post_syncvms",
        "label": "Post Sync VMs",
        "description": (
            "Executes at the end of a Sync VMs " "from Resource Handlers job."
        ),
        "job_type": "syncvms",
    },
    {
        "name": "pre_server_refresh",
        "label": "Pre Server Refresh",
        "description": (
            "Executes whenever a server's info is being refreshed "
            "based on data from the Resource Handler."
        ),
        "job_type": "syncvms",
    },
    {
        "name": "pre_provision",
        "label": "Pre-Provision",
        "description": "Executes at the beginning of a provisioning job.",
        "job_type": "provision",
    },
    {
        "name": "pre_create_resource",
        "label": "Pre-Create Resource",
        "description": "Executes after the CB server record is created, but before the VM is created",
        "job_type": "provision",
    },
    {
        "name": "pre_prov_engine_svr_creation",
        "label": "Pre-Provisioning Engine Server Creation",
        "description": "Executes after the VM and the CB server record are created, but before the provision engine record is created",
        "job_type": "provision",
    },
    {
        "name": "pre_poweron",
        "label": "Pre-Power-on",
        "description": "If provisioning the server through a provisioning engine such as "
        "Razor, then this executes after the VM, CB server "
        "record, and provision engine server record are created, but before the "
        "VM is powered on",
        "job_type": "provision",
    },
    {
        "name": "pre_networkconfig",
        "label": "Pre-Network Configuration",
        "description": "If the OS is deployed via a template, executes before CB configures the VM's network settings and the VM is powered on",
        "job_type": "provision",
    },
    {
        "name": "during_provisioning",
        "label": "During Resource Provisioning",
        "description": (
            "Certain Resource Handlers (currently only MAAS) may execute this during provisioning of the remote resource."
            "Action code should be specific to the Technology."
        ),
        "job_type": "provision",
    },
    {
        "name": "post_networkconfig",
        "label": "Post-Network Configuration",
        "description": (
            "Executes after CB configures the VM's network settings, but "
            "before the OS is confirmed ready or applications are installed"
        ),
        "job_type": "provision",
    },
    {
        "name": "network_verification",
        "label": "Network Verification",
        "description": (
            "Executes after the OS is ready and network has been "
            "configured, in order to verify networks"
        ),
        "job_type": "provision",
    },
    {
        "name": "post_network_verification",
        "label": "Post-Network Verification",
        "description": (
            "Executes after the server is up and ready and its network has been "
            "verified, before moving on to the next step"
        ),
        "job_type": "provision",
    },
    {
        "name": "pre_application",
        "label": "Pre-Application Installation",
        "description": (
            "If additional applications are being installed as part"
            " of the provision job, then this executes after the OS"
            " install is complete and network has been verified, "
            "but before CB kicks off any additional application installation"
        ),
        "job_type": "provision",
    },
    {
        "name": "post_provision",
        "label": "Post-Provision",
        "description": "Executes at the end of a provisioning job",
        "job_type": "provision",
    },
    {
        "name": "pre_install_apps_with_connector",
        "label": "Pre-Install Applications",
        "description": "Executes at the beginning of an install applications job",
        "job_type": "install_apps_with_connector",
    },
    {
        "name": "post_install_apps_with_connector",
        "label": "Post-Install Applications",
        "description": "Executes at the end of an install applications job",
        "job_type": "install_apps_with_connector",
    },
    {
        "name": "pre_uninstall_application",
        "label": "Pre-Uninstall Applications",
        "description": "Executes before an application is uninstalled using a connector",
        "job_type": "install_apps_with_connector",
    },
    {
        "name": "post_uninstall_application",
        "label": "Post-Uninstall Applications",
        "description": "Executes after an application is uninstalled using a connector",
        "job_type": "install_apps_with_connector",
    },
    {
        "name": "pre_decom",
        "label": "Pre-Delete",
        "description": "Executes at the beginning of a decommissioning job.",
        "job_type": "decom",
    },
    {
        "name": "post_decom",
        "label": "Post-Delete",
        "description": "Executes at the end of a decommissioning job.",
        "job_type": "decom",
    },
    {
        "name": "pre_servermodification",
        "label": "Pre-Server Modification",
        "description": "Executes at the beginning of a server modification job.",
        "job_type": "servermodification",
    },
    {
        "name": "post_servermodification",
        "label": "Post-Server Modification",
        "description": "Executes at the end of a server modification job.",
        "job_type": "servermodification",
    },
    {
        "name": "pre_expire",
        "label": "Pre-Expire Server",
        "description": "Executes at the beginning of a server expiration job",
        "job_type": "expire",
    },
    {
        "name": "post_expire",
        "label": "Post-Expire Server",
        "description": "Executes at the end of a server expiration job",
        "job_type": "expire",
    },
    {
        "name": "generated_hostname_overwrite",
        "label": "Generated Hostname Overwrite",
        "description": (
            "This allows any generated unique name that is going to be used in "
            "provision to be overwritten.  Useful when name uniqueness is an external "
            "function.  Note that a name returned in this orchestration point will "
            "still be subject to the validation orchestration if applicable."
        ),
        "job_type": "provision",
    },
    {
        "name": "validate_hostname",
        "label": "Validate Hostname",
        "description": (
            "If the provision job is setup to try generating unique names, actions "
            "here can be used to extend the validation functionality to external "
            "systems"
        ),
        "job_type": "provision",
    },
    {
        "name": "pre_functionaltest",
        "label": "Pre-CIT",
        "description": (
            "Executes at the beginning of a Continuous " "Infrastructure Testing job"
        ),
        "job_type": "functionaltest",
    },
    {
        "name": "post_functionaltest",
        "label": "Post-CIT",
        "description": (
            "Executes at the end of a Continuous Infrastructure " "Testing job"
        ),
        "job_type": "functionaltest",
    },
    # These show up as "No job type" in the UI:
    {
        "name": "blueprint",
        "label": "Blueprint Action",
        "description": "Executes during the deployment of one or more blueprints, related to build items",
    },
    {
        "name": "pre_job",
        "label": "Pre-Job",
        "description": "Executes at the beginning of every job",
    },
    {
        "name": "post_job",
        "label": "Post-Job",
        "description": "Executes at the end of every job",
    },
    {
        "name": "post_group_creation",
        "label": "Post Group Creation",
        "description": (
            "Executes after a new group is created. CB Plug-ins at this trigger point "
            'should have a run method that accepts a parameter named "group"'
        ),
    },
    {
        "name": "pre_group_modification",
        "label": "Pre Group Modification",
        "description": (
            "Executes before a group is saved. CB Plug-ins at this trigger point should have a "
            'run method that accepts an argument named "group" (the in-memory group with changes '
            'that have not yet been saved to the DB) and "existing_group" (the object as it exists in '
            "the DB). If any action at this point returns status FAILURE or raises an exception, "
            "the object will not be saved."
        ),
    },
    {
        "name": "post_group_modification",
        "label": "Post Group Modification",
        "description": (
            "Executes after a group is saved. CB Plug-ins at this trigger point "
            'should have a run method that accepts a parameter named "group"'
        ),
    },
    {
        "name": "post_environment_creation",
        "label": "Post Environment Creation",
        "description": (
            "Executes after a new environment is created. CB Plug-ins at this trigger point "
            'should have a run method that accepts a parameter named "environment". This trigger '
            "point can be useful for automatically setting up parameter options and other "
            "configuration on new environments."
        ),
    },
    {
        "name": "pre_environment_modification",
        "label": "Pre Environment Modification",
        "description": (
            "Executes before a environment is saved. CB Plug-ins at this trigger point "
            'should have a run method that accepts an argument named "environment" (the '
            "in-memory environment with changes that have not yet been saved to the DB) and "
            '"existing_environment" (the object as it exists in the DB). If any action at this point '
            "returns status FAILURE or raises an exception, the object will not be saved."
        ),
    },
    {
        "name": "post_environment_modification",
        "label": "Post Environment Modification",
        "description": (
            "Executes after a environment is saved. CB Plug-ins at this trigger point "
            'should have a run method that accepts a parameter named "environment"'
        ),
    },
    {
        "name": "pre_poweron_resource",
        "label": "Pre Power On",
        "description": (
            "Executes anytime a server is powered on from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "post_poweron_resource",
        "label": "Post Power On",
        "description": (
            "Executes anytime a server is powered on from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "pre_poweroff_resource",
        "label": "Pre Power Off",
        "description": (
            "Executes anytime a server is powered off from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "post_poweroff_resource",
        "label": "Post Power Off",
        "description": (
            "Executes anytime a server is powered off from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "pre_reboot_resource",
        "label": "Pre Reboot",
        "description": (
            "Executes anytime a server is rebooted from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "post_reboot_resource",
        "label": "Post Reboot",
        "description": (
            "Executes anytime a server is rebooted from CloudBolt "
            "(including during provisioning, server modification jobs, "
            "etc)"
        ),
    },
    {
        "name": "order_approval",
        "label": "Order Submission",
        "description": "Executes when an order is submitted",
    },
    {
        "name": "server_tier_validation",
        "label": "Server Tier Validation",
        "description": (
            """
            Executes while user is filling out an order form with a server tier. Add form field
            validation logic here, such as confirming values against external DNS or AD services.
        """
        ),
    },
    {
        "name": "blueprint_validation",
        "label": "Blueprint Validation",
        "description": (
            """
            Executes while user is filling out an order form. Add form field validation logic
            here, such as confirming values against external DNS or AD services.
        """
        ),
    },
    {
        "name": "post_order_denied",
        "label": "Post-Order Denied",
        "description": "Executes after an order is denied",
    },
    {
        "name": "pre_order_execution",
        "label": "Post-Order Approval",
        "description": "Executes after an order is approved and before jobs are created",
    },
    {
        "name": "post_order_execution",
        "label": "Post-Order Execution",
        "description": (
            "Executes after when an order is completed, it runs regardless of whether "
            "the order succeded or failed"
        ),
    },
    {
        "name": "waiting_for_config_manager_agent_checkin",
        "label": "Waiting for Config Manager Agent Checkin",
        "description": (
            "Executes when CB is waiting for results from a configuration "
            "manager's agent to check in."
        ),
    },
    {
        "name": "parameter_change",
        "label": "Parameter Change",
        "description": "Executes when ever a user changes a parameter on a server.",
    },
    {
        "name": "sso_user_update",
        "label": "SSO User Update",
        "description": ("Executes when a user logs in via an SSOProvider."),
    },
    {
        "name": "external_users_sync",
        "label": "External Users Sync",
        "description": (
            "Executes whenever external users synchronization takes "
            "place, including each time an external user logs in."
        ),
    },
    {
        "name": "generated_custom_field_options",
        "label": "Generated Parameter Options",
        "description": (
            "Management module used to control how optional values are presented for"
            " parameters.  Module must implement get_options_list."
        ),
    },
    {
        "name": "server_actions",
        "label": "Server Actions",
        "description": "List of custom server actions.",
    },
    {
        "name": "resource_actions",
        "label": "Resource Actions",
        "description": "List of custom resource actions.",
    },
    {
        "name": "pre_delete_resource",
        "label": "Pre-Delete Resource",
        "description": "Executes at the beginning of resource deletion.",
    },
    {
        "name": "post_delete_resource",
        "label": "Post-Delete Resource",
        "description": "Executes at the end of resource deletion.",
    },
    {
        "name": "validate_ip_address",
        "label": "Validate IP Address",
        "description": (
            'Validate IP address to be used for a given resource; takes "ip", '
            '"hostname" and "domain" as possible inputs.  This action will be '
            "executed when validating server IP during provisioning or when "
            "determining valid IPs from a network IP pool"
        ),
    },
    {
        "name": "compute_server_rate",
        "label": "Compute Server Rate",
        "description": (
            "Executes when calculating the cost of a projected or provisioned "
            "server. For a provisioned server, the calculated value is cached "
            "on the server object. It can be refreshed by running the Refresh "
            "Info action."
        ),
    },
    {
        "name": "validate_order_recipient",
        "label": "Validate Order Recipient",
        "description": (
            "Given a group of type Group and username of type str, this trigger "
            "executes when validating whether or not the username is permitted to "
            "receive an order for the Group. This trigger point is expected to "
            "return a Boolean."
        ),
    },
    # Terraform Hook Points
    {
        "name": "terraform_pre_provision",
        "label": "Terraform Pre-Provision",
        "description": (
            "Executes before creating resources via a Terraform Action. This "
            "trigger point is responsible for initializing state required by the "
            "downstream 'constructive' Terraform hooks."
        ),
    },
    {
        "name": "terraform_init",
        "label": "Terraform Init",
        "description": (
            "Executes when `terraform init` is called for the purpose of "
            "creating resources via a Terraform Action.\n"
            "Note that while `terraform init` is called before `terraform destroy`, "
            "this trigger point is exclusive to 'constructive' `terraform apply` "
            "executions."
        ),
    },
    {
        "name": "terraform_plan",
        "label": "Terraform Plan",
        "description": (
            "Executes when `terraform plan` is called for the purpose of "
            "creating resources via a Terraform Action.\n"
            "Note that while `terraform plan` is called before `terraform destroy`, "
            "this trigger point is exclusive to 'constructive' `terraform apply` "
            "executions."
        ),
    },
    {
        "name": "terraform_apply",
        "label": "Terraform Apply",
        "description": (
            "Executes when `terraform apply` is called for the purpose of "
            "creating resources via a Terraform Action."
        ),
    },
    {
        "name": "terraform_post_provision",
        "label": "Terraform Post-Provision ",
        "description": (
            "Executes after resources have been created via a Terraform Action. "
            "This trigger point can be used for integrating provisioned Resources "
            "with this platform, and performing any final teardown logic."
        ),
    },
    {
        "name": "terraform_provision_failure",
        "label": "Terraform Provision Failure ",
        "description": (
            "Executes if a failure occurs in any of 'constructive' actions."
        ),
    },
    {
        "name": "terraform_provision_cleanup",
        "label": "Terraform Provision Cleanup ",
        "description": (
            "Executes after `terraform apply` is called for the purpose of "
            "creating resources via a Terraform Action. Runs regardless of "
            "if the action succeeds or fails."
        ),
    },
    {
        "name": "terraform_pre_destroy",
        "label": "Terraform Pre-Destroy ",
        "description": (
            "Executes before deleting resources created via a Terraform Action. "
            "This trigger point is responsible for initializing state required by "
            "the downstream 'destructive' Terraform hooks."
        ),
    },
    {
        "name": "terraform_destroy",
        "label": "Terraform Destroy",
        "description": (
            "Executes when `terraform destroy` is called for the purpose of "
            "deleting resources created via a Terraform Action.\n"
            "Note that `terraform init` and `terraform plan` are implicitly called "
            "before running `terraform destroy`, but currently the behaviors of "
            "those subcommands are hard-coded for 'destructive' Terraform hooks."
        ),
    },
    {
        "name": "terraform_destroy_failure",
        "label": "Terraform Destroy Failure",
        "description": (
            "Executes after `terraform destroy` is called for the purpose of "
            "deleting resources created via a Terraform Action. Only runs if "
            "the action fails."
        ),
    },
    {
        "name": "terraform_post_destroy",
        "label": "Terraform Post-Destroy ",
        "description": (
            "Executes after all resources marked for deletion have been deleted "
            "successfully. This trigger point can be used performing any final "
            "teardown or verification logic."
        ),
    },
    {
        "name": "terraform_destroy_cleanup",
        "label": "Terraform Destroy Cleanup",
        "description": (
            "Executes after `terraform post-destroy` regardless of "
            "success or failure."
        ),
    },
]

hooks = [
    {
        "name": "Create virtual network",
        "description": "",
        "hook_point": "blueprint",
        "module": "cbhooks/hookmodules/create_virtual_network.py",
    },
    {
        "name": "Create Load Balancer",
        "description": (
            """
            Create a load balancer and add all servers in a particular tier.
            Also enables future scale up of the tier.
        """
        ),
        "hook_point": "blueprint",
        "module": "cbhooks/hookmodules/create_load_balancer.py",
    },
    {
        "name": "Delete Resource",
        "description": "Delete all servers in the resource and mark the resource as historical.",
        "hook_point": "resource_actions",
        "module": "cbhooks/hookmodules/delete_resource.py",
        "enabled": True,
        "hook_point_attributes": {
            "label": "Delete",
            "extra_classes": "icon-delete",
            "dialog_message": "This will delete all servers in the resource and then mark the "
            "resource as historical.",
            "submit_button_label": "Delete",
        },
    },
    {
        "name": "Scale Resource",
        "description": (
            "Add or remove servers in a specific tier and update the load "
            "balancer (if one exists)."
        ),
        "shared": True,
        "enabled": True,
        "hook_point": "resource_actions",
        "module": "cbhooks/hookmodules/scale_resource.py",
        "hook_point_attributes": {
            "label": "Scale",
            "extra_classes": "fas fa-arrows-alt-v",
            "dialog_message": (
                "Add/remove servers in a specific tier and reconfigure "
                "the load balancer as appropriate"
            ),
            "submit_button_label": "Scale",
            "list_view_visible": False,
        },
        "inputs": [
            {"name": "service_item", "label": "Tier", "namespace": "action_inputs"},
            {
                "name": "servers_to_add",
                "label": "Number of servers",
                "namespace": "action_inputs",
                "type": "INT",
                "minimum": -10,
                "maximum": 10,
            },
        ],
    },
    {
        "name": "Associate Servers",
        "description": (
            "Run as a Resource Action to associate existing CB servers with the resource as part of a "
            "specific tier. Purely representational, no actual changes made."
        ),
        "shared": True,
        "hook_point": "resource_actions",
        "module": "cbhooks/hookmodules/associate_servers_with_resource.py",
        "hook_point_attributes": {
            "label": "Associate Servers",
            "extra_classes": "far fa-object-group",
            "dialog_message": (
                "Associate existing CB servers with the resource as part of a "
                "specific tier. Purely representational, no actual changes made "
                "to the servers or any other component of the resource."
            ),
            "submit_button_label": "Associate",
            "list_view_visible": False,
        },
        "inputs": [
            {"name": "service_item", "label": "Tier", "namespace": "action_inputs"},
            {
                "name": "servers_to_associate",
                "label": "Servers to Associate",
                "namespace": "action_inputs",
            },
        ],
    },
    {
        "name": "Associate IPAM Networks",
        "description": (),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/associate_ipam_networks.py",
    },
    {
        "name": "User Update from SSO Provider",
        "description": (
            "Updates user's attributes based on information received from the "
            "SSO Provider when the user logs in."
        ),
        "hook_point": "sso_user_update",
        "module": "cbhooks/hookmodules/sso_user_update.py",
        "enabled": True,
    },
    {
        "name": "User Permission Sync From LDAP",
        "description": (
            "Updates user's permissions in CloudBolt based on the user's LDAP "
            "permissions. Configure how LDAP groups and OUs map to CloudBolt "
            "Groups and Roles on the LDAP settings page."
        ),
        "hook_point": "external_users_sync",
        "module": "cbhooks/hookmodules/external_users_sync.py",
        "enabled": True,
        # give existing actions priority by putting this action before them
        "hook_point_attributes": {"run_seq": 1},
    },
    {
        "name": "Join OU in AD Domain",
        "description": (
            "Adds a Windows server to a particular OU in an AD Domain, based on "
            "4 configured parameters for domain, ou, domain_username, and "
            "domain_password."
        ),
        "hook_point": "post_provision",
        "module": "cbhooks/hookmodules/join_domain_ou.py",
    },
    {
        "name": "Delete Server from LDAP",
        "description": (
            "Unregisters a server from LDAP pre-deletion. Requires having"
            "an LDAP Utility. Can use Domain to Join parameter or DNS Domain"
            "field of resource handler network information to determine correct"
            "LDAP Utility. If neither of those is configured appropriately, but"
            "there is only one LDAP Utility, it will be used as a default."
        ),
        "hook_point": "pre_decom",
        "module": "cbhooks/hookmodules/delete_server_from_ldap.py",
    },
    {
        "name": "Reboot Ubuntu servers",
        "description": (
            "Ensures the hostname on Ubuntu servers is propery set by "
            "rebooting the VM post network configuration. This hook is "
            "required for provisioning Ubuntu 14."
        ),
        "hook_point": "post_networkconfig",
        "module": "cbhooks/hookmodules/reboot_ubuntu_vm.py",
    },
    {
        "name": "Ping Test",
        "description": "Pings the IP from the CB server and checks whether a reply is received.",
        "hook_point": "network_verification",
        "module": "cbhooks/hookmodules/ping_test.py",
    },
    {
        "name": "SSH Public Key",
        "description": "Adds an SSH Public Key to a *nix server to enable password-less SSH.",
        "hook_point": "",
        "hook_type": "remote_script",
        "shared": True,
        "module": "cbhooks/hookmodules/ssh_public_key",
    },
    {
        "name": "Sample Pre-Create Resource Action",
        "description": "An example action that prefixes the hostname for the provisioning server with the first three letters of the server's group.",
        "hook_point": "pre_create_resource",
        "module": "cbhooks/hookmodules/pre_create_resource.py",
    },
    {
        "name": "Email Owners of Expired Servers",
        "description": (
            "This hook will send one email to each user who has expired server(s) with a list of "
            "their server(s) that are expired.  Users will receive one email per day until they "
            "delete their servers.  If you would like to customize the email message sent, edit "
            "the email template titled 'Expired Server'."
        ),
        "hook_point": "pre_expire",
        "module": "cbhooks/hookmodules/email_expired_server_owners.py",
    },
    {
        "name": "Internal CloudBolt Hook",
        "description": "This action manages option list for all out of the box 'generated options' parameters",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/__cloudbolt_generated_options_default_hook.py",
        "enabled": True,
        "custom_fields": [
            "vmware_disk_type",
            "domain_to_join",
            "aws_elastic_ip",
            "os_floating_ip",
            "time_zone",
            "oracle_ip_reservation",
        ],
    },
    {
        "name": "Set deleteOnTermination on AWS EBS Volumes",
        "description": "This action allows you to manage EBS volumes, setting them up to be deleted by AWS "
        "when the attached instance is deleted. "
        "Whenever there is a change in the out-of-the-box parameter "
        "'Auto-delete EBS volumes on termination', this action is triggered. It sets the value for "
        "'deleteOnTermination' on each of the instance's attached volumes. When set "
        "to True, the volumes will be deleted from AWS automatically when the instance is terminated.",
        "hook_point": "parameter_change",
        "module": "cbhooks/hookmodules/set_deleteontermination_on_ebs_volumes.py",
        "enabled": True,
        "custom_fields": ["delete_ebs_volumes_on_termination"],
    },
    {
        "name": "List Azure Availability Set options for Resource Group",
        "description": "Gets the availability sets for the selected azure resource group.",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/generate_azure_availability_set_options.py",
        "enabled": True,
        "custom_fields": ["availability_set_arm"],
    },
    {
        "name": "List available azure node sizes based on storage type",
        "description": "Limits the choice of node size based on which nodes will boot with the given storage type",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/limit_azure_node_size_by_storage_type.py",
        "enabled": True,
        "custom_fields": ["node_size"],
    },
    {
        "name": "List Azure Storage Type options",
        "description": "Only includes the UltraSSD_LRS storage type when adding a Data Disk to an existing VM",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/limit_azure_storage_type_options.py",
        "enabled": True,
        "custom_fields": ["storage_account_type_arm"],
    },
    {
        "name": "List Data Protection Plan options",
        "description": "Queries the available data protection plans provided by connected backends",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/dataprotection/list_dataprotection_plans.py",
        "enabled": True,
        "custom_fields": ["dataprotection_plan"],
    },
    {
        "name": "Net Options as Env/Group Intersection",
        "description": "Generates network options as intersection of group and environment options",
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/group_env_net_intersection.py",
        "custom_fields": [
            "sc_nic_0",
            "sc_nic_1",
            "sc_nic_2",
            "sc_nic_3",
            "sc_nic_4",
            "sc_nic_5",
            "sc_nic_6",
            "sc_nic_7",
            "sc_nic_8",
            "sc_nic_9",
        ],
    },
    {
        "name": "Validate IP Address (nslookup)",
        "description": ("A sample action that uses nslookup to validate an IP address"),
        "hook_point": "validate_ip_address",
        "module": "cbhooks/hookmodules/validate_ip_address.py",
    },
    {
        "name": "Validate IP Address is not pingable",
        "description": (
            "A sample action that validates an IP address is not already pingable"
        ),
        "enabled": True,
        "hook_point": "validate_ip_address",
        "module": "cbhooks/hookmodules/validate_ip_address_not_pingable.py",
    },
    {
        "name": "Ad Hoc Script",
        "description": ("An action that supports running ad hoc scripts on servers"),
        "hook_point": "server_actions",
        "enabled": True,
        "module": "cbhooks/hookmodules/ad_hoc_script",
        "hook_type": "remote_script",
        "hook_point_attributes": {
            "label": "Ad Hoc Script",
            "extra_classes": "fas fa-code",
        },
        "inputs": [
            {
                "name": "script_contents",
                "label": "Script Contents",
                "description": (
                    "The contents of the ad hoc script you would like to run"
                ),
                "type": "CODE",
                "namespace": "action_inputs",
            }
        ],
    },
    {
        "name": "create_snapshot",
        "description": ("Server Action to create snapshot for an OpenStack Instance."),
        "hook_point": "server_actions",
        "enabled": True,
        "module": "cbhooks/hookmodules/create_snapshot.py",
        "hook_point_attributes": {
            "label": "Create Snapshot",
            "extra_classes": "fas fa-camera",
            "dialog_message": "Create new snapshot of VM at the current location? This action allows you to save the state of the server so it is possible to revert to it at a later time. After the snapshot is created, the existing snapshots created by CB will be permanently deleted.",
        },
        "resource_technologies": ["OpenStack"],
        "inputs": [
            {
                "name": "snapshot_name",
                "label": "Snapshot Name",
                "description": ("Name of new Snapshot"),
                "type": "STR",
                "namespace": "action_inputs",
            }
        ],
    },
    {
        "name": "revert_to_snapshot",
        "description": (
            "Server Action to revert server to the most recent snapshot created by CB."
        ),
        "hook_point": "server_actions",
        "enabled": True,
        "module": "cbhooks/hookmodules/revert_to_snapshot.py",
        "hook_point_attributes": {
            "label": "Revert To Snapshot",
            "extra_classes": "fas fa-undo",
            "dialog_message": " The action reverts VM to the latest snapshot create by CB.",
        },
        "resource_technologies": ["OpenStack"],
    },
    {
        "name": "Resize VM",
        "enabled": True,
        "description": ("Resize the VM"),
        "hook_point": "server_actions",
        "module": "cbhooks/hookmodules/resize_vm.py",
        "hook_point_attributes": {
            "label": "Resize VM",
            "extra_classes": "fas fa-arrows",
        },
        "resource_technologies": ["Azure"],
        "inputs": [
            {
                "name": "new_size",
                "label": "New Size",
                "description": ("The new machine size"),
                "type": "STR",
                "namespace": "action_inputs",
            }
        ],
    },
    {
        "name": "Download CloudBolt Upgrader",
        "description": "",
        "hook_point": "",
        "module": "cbhooks/hookmodules/download_cloudbolt_upgrader.py",
    },
    {
        "name": "Sample NAT IP Translation Action",
        "description": (
            "This action is a sample of what can be done at the Pre "
            "Server Refresh trigger point. It uses the NAT Info "
            "field on networks to translate IP addresses by "
            "replacing the first 3 octets with those from the "
            "NAT Info."
        ),
        "hook_point": "pre_server_refresh",
        "module": "cbhooks/hookmodules/sample_nat_ip_translation_action.py",
    },
    {
        "name": "Sample Per-User Server Limits Action",
        "description": (
            "A sample pre-provision action that prevents a user from provisioning "
            "when doing so would cause the number of servers they own to exceed "
            "the given limit."
        ),
        "hook_point": "pre_provision",
        "module": "cbhooks/hookmodules/sample_per_user_server_limits_action.py",
        "inputs": [
            {
                "name": "max_servers_per_user",
                "label": "Max Servers Per User",
                "description": (
                    "The maximum number of servers each user should "
                    "be allowed to own in CloudBolt"
                ),
                "type": "INT",
                "namespace": "action_inputs",
            }
        ],
        "mappings": {"max_servers_per_user": 10},
    },
    {
        "name": "Automatically decom server when provisioning fails",
        "description": (
            "Sample action automatically decommissions server if its provision job fails."
        ),
        "hook_point": "post_provision",
        "module": "cbhooks/hookmodules/post_prov_failure_auto_decom_server.py",
        "enabled": False,
        "run_on_statuses": "FAILURE,CANCELED",
    },
    {
        "name": "puppet_ent_2015.3_auto_install_agent",
        "description": (
            "Used by Puppet Enterprise 2015.3 to boostrap a puppet agent onto "
            "the node being provisioned and do some initial setup."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_auto_install_agent.py",
    },
    {
        "name": "puppet_ent_2015.3_sign_cert",
        "description": (
            "This is a dependency run-once method using token auth to set the "
            "generated certname in the whitelist Puppet Ent provides modules "
            "with parameters to properly setup the whitelist A puppet run is "
            "required on the master to complete this configuration"
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_sign_cert.py",
    },
    {
        "name": "puppet_ent_2015.3_delete_server_from_connector",
        "description": (
            "Used by Puppet Enterprise 2015.3 to remove a node "
            "during decommissioning."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_delete_server_from_connector.py",
    },
    {
        "name": "puppet_ent_2015.3_discover_groups",
        "description": (
            "Used by Puppet Enterprise 2015.3 to determine which groups are "
            "available in PE and make PEGroup objects for them."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_discover_groups.py",
    },
    {
        "name": "puppet_ent_3.X_auto_install_agent",
        "description": (
            "Used by Puppet Enterprise 3.X to boostrap a puppet agent onto "
            "the node being provisioned and do some initial setup."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_3.X_auto_install_agent.py",
    },
    {
        "name": "puppet_ent_3.X_delete_server_from_connector",
        "description": (
            "Used by Puppet Enterprise 3.X to remove a node " "during decommissioning."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_3.X_delete_server_from_connector.py",
    },
    {
        "name": "puppet_ent_3.X_discover_groups",
        "description": (
            "Used by Puppet Enterprise 3.X to determine which groups are "
            "available in PE and make PEGroup objects for them."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_3.X_discover_groups.py",
    },
    {
        "name": "puppet_ent_2015.3_get_node_facts",
        "description": (
            "Used by Puppet Enterprise 2015.3 to retrieve facts for a node, used by the connector "
            "when synchronizing servers."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_get_node_facts.py",
    },
    {
        "name": "puppet_ent_3.X_get_node_facts",
        "description": (
            "Used by Puppet Enterprise 3.X to retrieve facts for a node, used by the connector "
            "when synchronizing servers."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_3.X_get_node_facts.py",
    },
    {
        "name": "puppet_ent_2015.3_clean_cert",
        "description": "Used by Puppet Enterprise 2015.3 to delete a node from the puppet master.",
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_2015.3_clean_cert.py",
    },
    {
        "name": "puppet_ent_3.X_clean_cert",
        "description": "Used by Puppet Enterprise 3.X to delete a node from the puppet master.",
        "hook_point": None,
        "module": "cbhooks/hookmodules/puppet/puppet_ent_3.X_clean_cert.py",
    },
    {
        "name": "ansible_run_adhoc_command",
        "description": (
            "Used by Ansible to run ad-hoc commands on a server or servers."
        ),
        "hook_point": "server_actions",
        "enabled": False,
        "module": "cbhooks/hookmodules/ansible/run_adhoc_command.py",
        "hook_point_attributes": {
            "label": "Ansible: Run Ad-hoc Command",
            "extra_classes": "fas fa-play",
        },
        "inputs": [
            {
                "name": "module",
                "label": "Module",
                "description": ("The module you would like to run"),
                "type": "STR",
                "namespace": "action_inputs",
            },
            {
                "name": "module_arguments",
                "label": "Arguments",
                "description": ("Arguments to pass to the module"),
                "type": "STR",
                "namespace": "action_inputs",
                "required": False,
            },
        ],
    },
    {
        "name": "ansible_run_playbook",
        "description": (
            "Used by Ansible to run playbooks on a server, a list of servers, "
            "or an inventory group."
        ),
        "hook_point": "server_actions",
        "enabled": False,
        "module": "cbhooks/hookmodules/ansible/run_playbook.py",
        "hook_point_attributes": {
            "label": "Ansible: Run Playbook",
            "extra_classes": "fas fa-play",
        },
        "inputs": [
            {
                "name": "playbook_path",
                "label": "Playbook",
                "description": ("The playbook you would like to run"),
                "type": "STR",
                "namespace": "action_inputs",
            }
        ],
    },
    #
    # Load Balancer actions
    #
    # -- Base actions --
    {
        "name": "construct_load_balancer",
        "description": (
            "Used by blueprint deployment to configure a resource handler based "
            "load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/construct_load_balancer.py",
    },
    {
        "name": "destroy_load_balancer",
        "description": (
            "Used by blueprint deployment to destroy a resource handler based "
            "load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/destroy_load_balancer.py",
    },
    {
        "name": "add_members_to_load_balancer",
        "description": (
            "Used by blueprint deployment to add servers to a resource handler based "
            "load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/add_members_to_load_balancer.py",
    },
    {
        "name": "remove_members_from_load_balancer",
        "description": (
            "Used by blueprint deployment to remove servers from a resource handler "
            "based load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/remove_members_from_load_balancer.py",
    },
    # -- HA Proxy --
    {
        "name": "haproxy_construct_load_balancer",
        "description": (
            "Used by blueprint deployment to configure a linux server as an "
            "HA Proxy Load Balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/haproxy_construct_load_balancer.py",
        "inputs": [
            {
                "name": "haproxy_tier",
                "label": "HA Proxy Tier",
                "namespace": "action_inputs",
            },
            {
                "name": "install_haproxy",
                "label": "Install HA Proxy",
                "namespace": "action_inputs",
                "type": "BOOL",
            },
        ],
    },
    {
        "name": "haproxy_add_members_to_load_balancer",
        "description": (
            "Used by blueprint deployment to add servers to a haproxy configured "
            "load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/haproxy_add_members_to_load_balancer.py",
    },
    {
        "name": "haproxy_remove_members_from_load_balancer",
        "description": (
            "Used by blueprint deployment to remove servers from a haproxy configured "
            "load balancer."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/haproxy_remove_members_from_load_balancer.py",
    },
    # -- F5 LoadBalancer --
    {
        "name": "f5_construct_load_balancer",
        "description": (
            "Used by blueprint deployment to configure a new virtual pool in an "
            "F5 load balancer appliance."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/f5_construct_load_balancer.py",
        "inputs": [
            {
                "name": "virtual_server_name_template",
                "label": "VIP Name Template",
                "namespace": "action_inputs",
                "required": False,
            },
            {
                "name": "lb_method",
                "label": "Load balancing Method",
                "namespace": "action_inputs",
            },
            {
                "name": "f5_appliance_id",
                "label": "F5 Big-IP Appliance",
                "namespace": "action_inputs",
            },
        ],
    },
    {
        "name": "f5_destroy_load_balancer",
        "description": (
            "Used by blueprint deployment to destroy the appropriate virtual pool in "
            "an F5 load balancer appliance."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/f5_destroy_load_balancer.py",
    },
    {
        "name": "f5_add_members_to_load_balancer",
        "description": (
            "Used by blueprint deployment to add servers to the appropriate pool in an "
            "F5 load balancer appliance."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/f5_add_members_to_load_balancer.py",
    },
    {
        "name": "f5_remove_members_from_load_balancer",
        "description": (
            "Used by blueprint deployment to remove servers from the appropriate pool "
            "in an F5 load balancer appliance."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/load_balancers/f5_remove_members_from_load_balancer.py",
    },
    #
    # Legacy Infoblox hooks
    #
    {
        "name": "Infoblox 00 - Validate that FQDN is unique",
        "description": (
            "LEGACY: A pre-9.0 sample action that checks infoblox for the existence of a given a FQDN"
        ),
        "hook_point": "validate_hostname",
        "module": "cbhooks/hookmodules/infoblox/validate_hostname.py",
    },
    {
        "name": "Infoblox 01 - Calculate FQDN and Allocate IP",
        "description": (
            "LEGACY: A pre-9.0 sample action that allocates an IP in infoblox, given a server FQDN"
        ),
        "hook_point": "pre_create_resource",
        "module": "cbhooks/hookmodules/infoblox/allocate_ip.py",
    },
    {
        "name": "IPAM Associations 01 - Allocate IP From Associated IPAM",
        "description": (
            "LEGACY: A pre-9.0 action that will attempt to allocate an IP address from ",
            "one of the associated IPAM networks using the first ",
            "successfully allocated address. This plug-in assumes you ",
            "have already associated your CloudBolt network with all "
            "pertinent IPAM networks",
        ),
        "hook_point": "pre_create_resource",
        "module": "cbhooks/hookmodules/infoblox/allocate_ip_from_associated_ipams.py",
    },
    {
        "name": "Infoblox 02 - Setup DHCP for Host",
        "description": (
            "LEGACY: A pre-9.0 sample action that registers a server's mac address with infoblox "
            "and restarts the DHCP services so the setting takes afect before "
            "the new server is powered on for the first time"
        ),
        "hook_point": "pre_networkconfig",
        "module": "cbhooks/hookmodules/infoblox/setup_dhcp_for_host.py",
    },
    {
        "name": "Infoblox 03 - Make sure server IP matches Infoblox record",
        "description": (
            "LEGACY: A pre-9.0 sample action that will ensure that a server IP matches the entry "
            "for that server in infoblox, prior to intalling a ConfigManager agent"
        ),
        "hook_point": "pre_application",
        "module": "cbhooks/hookmodules/infoblox/set_infoblox_ip_on_server.py",
    },
    {
        "name": "Infoblox 04 - Delete host record",
        "description": (
            "LEGACY: A pre-9.0 sample action that de-allocates an IP in infoblox by deleting the "
            "host record"
        ),
        "hook_point": "post_decom",
        "module": "cbhooks/hookmodules/infoblox/delete_host_from_infoblox.py",
    },
    #
    # OOTB Infoblox Hook
    #
    {
        "name": "Infoblox Plug-in",
        "hook_point": None,
        "hook_type": "ipam_hook",
        "module": "cbhooks/hookmodules/ipam/infoblox.py",
        "ipam_technology": "Infoblox",
    },
    #
    # OOTB phpIPAM Hook
    #
    {
        "name": "phpIPAM Plug-in",
        "hook_point": None,
        "hook_type": "ipam_hook",
        "module": "cbhooks/hookmodules/ipam/phpipam.py",
        "ipam_technology": "phpIPAM",
    },
    #
    # OOTB BlueCat Hook
    #
    {
        "name": "BlueCat Plug-in",
        "hook_point": None,
        "hook_type": "ipam_hook",
        "module": "cbhooks/hookmodules/ipam/bluecat.py",
        "ipam_technology": "BlueCat",
    },
    #
    # OOTB SolarWinds Hook
    #
    {
        "name": "SolarWinds Plug-in",
        "hook_point": None,
        "hook_type": "ipam_hook",
        "module": "cbhooks/hookmodules/ipam/solarwindsipam.py",
        "ipam_technology": "SolarWinds",
    },
    # Cohesity Data Protection Hook
    {
        "name": "Cohesity Plug-in",
        "hook_point": None,
        "hook_type": "dataprotection_hook",
        "module": "cbhooks/hookmodules/dataprotection/cohesity.py",
        "dataprotection_technology": "Cohesity",
    },
    # Rubrik Data Protection Hook
    {
        "name": "Rubrik Plug-in",
        "hook_point": None,
        "hook_type": "dataprotection_hook",
        "module": "cbhooks/hookmodules/dataprotection/rubrik.py",
        "dataprotection_technology": "Rubrik",
    },
    # Azure Backup Data Protection Hook
    {
        "name": "Azure Backup Plug-in",
        "hook_point": None,
        "hook_type": "dataprotection_hook",
        "module": "cbhooks/hookmodules/dataprotection/azure_backup.py",
        "dataprotection_technology": "Azure Backup",
    },
    # CommVault Data Protection Hook
    {
        "name": "CommVault Plug-in",
        "hook_point": None,
        "hook_type": "dataprotection_hook",
        "module": "cbhooks/hookmodules/dataprotection/commvault.py",
        "dataprotection_technology": "CommVault",
    },
    # OOTB ITSM.ServiceNow Hook
    {
        "name": "ServiceNow ITSM CMDB Plug-in",
        "hook_point": None,
        "hook_type": "itsm_hook",
        "module": "cbhooks/hookmodules/itsm/servicenow/cmdb.py",
        "itsm_technology": "ServiceNow",
        "action": "cmdb",
    },
    # Options for Server Lock
    {
        "name": "Generate Options for Server Lock",
        "description": (
            "Generates options for the Server Lock parameter used to "
            "prevent actions on servers"
        ),
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/generate_options_for_server_lock.py",
        "enabled": True,
        "custom_fields": ["server_lock"],
    },
    # Discovery helpers
    {
        "name": "Discover Linux Info",
        "description": (
            "Executes a remote script to discover hostname, CPUs, etc., then updates the server "
            "record in CB."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/rules/actions/discover_linux_info.py",
    },
    {
        "name": "Discover Windows Info",
        "description": (
            "Executes a remote script to discover hostname, CPUs, etc., then updates the server "
            "record in CB."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/rules/actions/discover_windows_info.py",
    },
    # Sample rate hooks
    {
        "name": "AWS Rate Hook",
        "description": "Calculate server rate using Amazon pricing data",
        "hook_point": "compute_server_rate",
        "module": "cbhooks/hookmodules/rates/aws_rate_hook.py",
        "enabled": True,
        "resource_technologies": ["Amazon Web Services", "AWS GovCloud (US)"],
    },
    {
        "name": "GCE Rate Hook",
        "description": "Calculate server rate using Google pricing data",
        "hook_point": "compute_server_rate",
        "module": "cbhooks/hookmodules/rates/gce_rate_hook.py",
        "enabled": True,
        "resource_technologies": ["Google Compute Engine"],
    },
    {
        "name": "GCP Rate Hook",
        "description": "Calculate server rate using Google pricing data",
        "hook_point": "compute_server_rate",
        "module": "cbhooks/hookmodules/rates/gcp_rate_hook.py",
        "enabled": True,
        "resource_technologies": ["Google Cloud Platform"],
    },
    {
        "name": "Validate GCP network selection",
        "description": "Ensure that any selected networks on the GCP order form are available to the selected Zone.",
        "hook_point": "server_tier_validation",
        "module": "cbhooks/hookmodules/validate_gcp_network_selection.py",
        "enabled": True,
        "resource_technologies": ["Google Cloud Platform"],
    },
    {
        "name": "Validate Azure Availability Sets and Zones",
        "description": "Ensure that values for both an Availability Set and an Availability Zone aren't provided.",
        "hook_point": "server_tier_validation",
        "module": "cbhooks/hookmodules/validate_azure_availability_sets_and_zones.py",
        "enabled": True,
        "resource_technologies": ["Azure"],
    },
    {
        "name": "Validate Azure Storage Account Type",
        "description": "Ensure that auto-created storage accounts use a valid storage account type.",
        "hook_point": "server_tier_validation",
        "module": "cbhooks/hookmodules/validate_azure_storage_account_type.py",
        "enabled": True,
        "resource_technologies": ["Azure"],
    },
    {
        "name": "Azure Resource Manager Rate Hook",
        "description": "Calculate server rate using Microsoft pricing data",
        "hook_point": "compute_server_rate",
        "module": "cbhooks/hookmodules/rates/azure_arm_rate_hook.py",
        "enabled": True,
        "resource_technologies": ["Azure"],
    },
    # Billing-related
    {
        "name": "Download Azure Resource Manager Invoice",
        "description": "Download the latest monthly invoice for all Azure ARM Resource Handlers.",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/download_azure_invoices.py",
    },
    {
        "name": "Download Azure rate card",
        "description": "Download the latest rate card for Azure pricing information",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/download_azure_rate_card.py",
    },
    {
        "name": "Import Public Cloud Billing Data",
        "description": "Download last month's billing data for the pub cloud providers and add "
        "any server-related costs to the CB DB.",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/import_pub_cloud_billing_data.py",
    },
    {
        "name": "Refresh All Server Utilization",
        "description": """
            Run any action whose name starts with "Refresh Utilization ".
            This action can be set up to run periodically via Admin > Recurring Jobs.
        """,
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_all.py",
    },
    {
        "name": "Refresh Server Rates",
        "description": """
            Checks for updates in the Amazon Web Services and Google Compute Engine rates.
            If there are updates on either, will download the rate files and update rates on servers
            from the new rate data.
            ** For this job to be able to compute rates on your servers, you must have rate hooks enabled.
            To check, go to 'Admin' > 'Orchestration Actions', select Job/Process = 'Other' and scroll to the section
            'Compute Server Rates'. From here, you can enable the AWS and GCE rate hooks.**
        """,
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/refresh_server_rates.py",
    },
    {
        "name": "Download Currency Exchange Rates",
        "description": "Download the latest exchange rates for supported currencies.",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/download_exchange_rates.py",
    },
    {
        "name": "Delete Old Job Records",
        "description": (
            "Find any job record in the database older than the threshold "
            "and delete it, also removing its log file from disk."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/delete_old_job_records.py",
    },
    {
        # This action will be executed by the Refresh All Server Utilization recurring job.
        # It runs all actions having name "Refresh Utilization *".
        "name": "Refresh Utilization for Acropolis Servers",
        "description": "Query Acroplis for VM utilization and update server stats",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_utilization_acropolis.py",
    },
    {
        # This action will be executed by the Refresh All Server Utilization recurring job.
        # It runs all actions having name "Refresh Utilization *".
        "name": "Refresh Utilization for VMware Servers",
        "description": "Query vCenter for VM utilization and update server stats",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_utilization_vmware.py",
    },
    {
        # This action will be executed by the Refresh All Server Utilization recurring job.
        # It runs all actions having name "Refresh Utilization *".
        "name": "Refresh Utilization for AWS Servers",
        "description": "Query AWS for VM utilization and update server stats",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_utilization_aws.py",
    },
    {
        # This action will be executed by the Refresh All Server Utilization recurring job.
        # It runs all actions having name "Refresh Utilization *".
        "name": "Refresh Utilization for Azure ARM Servers",
        "description": "Query Azure for VM utilization and update server stats",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_utilization_azure.py",
    },
    {
        # This action will be executed by the Refresh All Server Utilization recurring job.
        # It runs all actions having name "Refresh Utilization *".
        "name": "Refresh Utilization for GCP Servers",
        "description": "Query GCP for VM utilization and update server stats",
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/server_utilization/refresh_utilization_gcp.py",
    },
    {
        "name": "Update Search Index",
        "description": """
        Refreshes the search index that enables the global search feature.
        """,
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/update_search_index.py",
    },
    {
        "name": "Auto-power control servers",
        "description": (
            "This plug-in enables auto-powering off of servers for periods of the day. This can be useful for "
            "servers that do not need to run at night, to save on public cloud costs/resource consumption at "
            "those times of the day."
            "\n\n"
            "To use this feature, go to a server's details page and configure a power "
            "schedule on the tab or use the Power Schedule parameter at order time. "
            "When this action runs it will look for the ScheduledTime models "
            "created by you setting the power schedule, and use them to determine which "
            "servers should be powered on or off at the current time. "
            "\n\n"
            "CloudBolt will use its own server time to judge whether it is the right time to power on and "
            "off VMs, so make sure you know what time it is on the CB server and that the timezone is right. "
            "\n\n"
            "Also note that the recurring job that runs this action is expected to be run "
            "every hour on the hour. If it is run on a different schedule, that will impact "
            "when servers are powered on or off. The power change will only happen if the job runs "
            "during the hour on the day when a power change is scheduled."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/recurring_power_for_servers.py",
    },
    {
        "name": "Auto-power control resources",
        "description": (
            "This plug-in enables auto-powering off of resources' servers for periods of the day. "
            "It uses the deploy sequence of servers originally set in the blueprint for a given resource to determine "
            "the order in which servers will power on or off. "
            "The servers will be shown in the resource's 'Server' tab in the same sequence they were provisioned in. "
            "When powering off servers, the reverse order from the deploy sequence will be used. "
            "\n\n"
            "You can manage this power schedule from the 'Power Schedule' tab on any resource that has servers. "
            "\n\n"
            "Also note that the recurring job that runs this action is expected to be run "
            "every hour on the hour. If it is run on a different schedule, that will impact "
            "when servers are powered on or off. The power change will only happen if the job runs "
            "during the hour on the day when a power change is scheduled."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/recurring_power_for_resources.py",
    },
    {
        "name": "Sample server tier validation plugin",
        "description": "Illustrates potential uses for custom validation of the New Server form",
        "hook_point": "server_tier_validation",
        "module": "cbhooks/hookmodules/sample_order_validation.py",
        "enabled": False,
    },
    {
        "name": "Sample blueprint validation plugin",
        "description": "Illustrates potential uses for custom validation of an order form",
        "hook_point": "blueprint_validation",
        "module": "cbhooks/hookmodules/sample_blueprint_validation.py",
        "enabled": False,
    },
    {
        "name": "Two Approvers",
        "description": (
            "Overrides CloudBolt's standard Order Approval workflow, requiring "
            "two users to approve an Order before it becomes Active."
        ),
        "hook_point": "pre_order_execution",
        "module": "cbhooks/hookmodules/two_approvers.py",
        "enabled": False,
    },
    {
        "name": "Clean RH Networks & Templates",
        "description": """
            Cleans up any networks or templates in CB that are no longer valid
            by syncing with what is on the Resource Handler.
            This action can be set to run periodically via Admin > Recurring Jobs.
        """,
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/clean_rh_networks_templates.py",
    },
    {
        "name": "Reboot Server(s)",
        "description": """
            Sample action that can be used in various contexts to reboot the
            server(s) available to that context, or modified to reboot some subset thereof.
        """,
        "shared": True,
        "hook_point": None,
        "module": "cbhooks/hookmodules/reboot_server.py",
    },
    {
        "name": "Edit Kubernetes object",
        "description": (
            "Modifies an object in a Kubernetes cluster, like the `kubectl "
            "edit` CLI command. Runs via the Edit button on the cluster's "
            "Deployed Objects tab or a resource's Kubernetes tab."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/kubernetes/edit_kubernetes_object.py",
    },
    {
        "name": "Sync Resources",
        "description": (
            "For any Blueprint that has a Discovery Plug-in specified, "
            "use that logic to discover and sync Resources of the type "
            "described by that Blueprint."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/sync_resources.py",
    },
    {
        "name": "Chef Agent Bootstrap",
        "description": ("Bootstraps Chef Agent on the provisioned server."),
        "hook_point": None,
        "module": "cbhooks/hookmodules/chef/chef_bootstrap_agent.py",
    },
    {
        "name": "Chef Remove Node",
        "description": ("Removes node from Chef and removes client."),
        "hook_point": None,
        "module": "cbhooks/hookmodules/chef/chef_remove_node.py",
    },
    {
        "name": "Refresh Blueprints from Remote Source",
        "description": (
            "For any Blueprint that is configured to be populated from a definition "
            "stored in a remote source location, refresh that Blueprint using the "
            "Remote Source URL that is set on it."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/refresh_remote_source_bps.py",
    },
    {
        "name": "ServiceNow CMDB - CI Create Hook",
        "description": (
            "Action to call into ServiceNow to create a new CI entry "
            "based on provisioning parameters"
        ),
        "hook_point": "post_provision",
        "module": "cbhooks/hookmodules/create_service_now_ci.py",
    },
    {
        "name": "ServiceNow CMDB - CI Delete Hook",
        "description": (
            "A sample action to call into ServiceNow to Delete the CI entry "
            "for each server that was deleted as part of the decommission "
            "job"
        ),
        "hook_point": "post_decom",
        "module": "cbhooks/hookmodules/delete_service_now_ci.py",
    },
    {
        "name": "ServiceNow Order Submit",
        "description": (
            'Sends Order data to ServivceNow "sc_request" table '
            "Add response.snow_order_submit_sys_id to CustomFieldValue "
            ""
        ),
        "hook_point": "order_approval",
        "module": "cbhooks/hookmodules/servicenow_order_submit.py",
        "enabled": False,
    },
    {
        "name": "Sync CloudBolt Order Status with ServiceNow Catalog Request Status",
        "description": (
            "Get list of current pending orders and check the status"
            'in ServiceNow. If status has changed to "approved" or "rejected",'
            "change CB order status accordingly."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/recurring_jobs/servicenow_request_queue.py",
    },
    #
    # OOTB ServiceNow Hook
    #
    {
        "name": "ServiceNow CMDB Plug-in",
        "hook_point": None,
        "hook_type": "servicenow_hook",
        "module": "cbhooks/hookmodules/servicenow/servicenow_cmdb.py",
        "action": "cmdb",
    },
    {
        "name": "ServiceNow Order Plug-in",
        "hook_point": None,
        "hook_type": "servicenow_hook",
        "module": "cbhooks/hookmodules/servicenow/servicenow_order.py",
        "action": "order",
    },
    # CONTENT LIBRARY CACHING
    {
        "name": "Content Library Caching",
        "description": "Save local copies of the content hosted by CloudBolt to speed up the page",
        "hook_point": None,
        "module": "cbhooks/hookmodules/content_library/cache_content.py",
    },
    {
        "name": "Remote Script With WinRM",
        "description": (
            "Executes remote script on Windows Server with "
            "WinRM. Modify this action for additional customization."
        ),
        "hook_point": None,
        "module": "cbhooks/hookmodules/remote_scripts_with_winrm.py",
    },
    # Terraform
    {
        "name": "Run Pre-Provision Terraform",
        "description": (
            "Perform setup logic before executing 'constructive' Terraform "
            "subcommands (e.g. `init` `plan`, and `apply`)."
        ),
        "hook_point": "terraform_pre_provision",
        "module": "cbhooks/hookmodules/terraform/pre_provision.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Init",
        "description": (
            "Defines the behavior that CloudBolt uses when calling the underlying "
            "`terraform init` command."
        ),
        "hook_point": "terraform_init",
        "module": "cbhooks/hookmodules/terraform/init.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Plan",
        "description": (
            "Defines the behavior that CloudBolt uses when calling the underlying "
            "`terraform plan` command."
        ),
        "hook_point": "terraform_plan",
        "module": "cbhooks/hookmodules/terraform/plan.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Apply",
        "description": (
            "Defines the behavior that CloudBolt uses when calling the underlying "
            "`terraform apply` command."
        ),
        "hook_point": "terraform_apply",
        "module": "cbhooks/hookmodules/terraform/apply.py",
        "enabled": True,
    },
    {
        "name": "Run Post-Provision Terraform",
        "description": (
            "Perform teardown and integration logic after executing 'constructive' "
            "Terraform subcommands (e.g. `init`, `plan`, and `apply`)."
        ),
        "hook_point": "terraform_post_provision",
        "module": "cbhooks/hookmodules/terraform/post_provision.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Provision Failure",
        "description": (
            "Perform cleanup logic after a failed 'constructive' Terraform "
            "subcommand (e.g. `init`, `plan`, and `apply`)."
        ),
        "hook_point": "terraform_provision_failure",
        "module": "cbhooks/hookmodules/terraform/provision_failure.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Provision Cleanup",
        "description": (
            "Perform cleanup logic after executing 'constructive' Terraform "
            "subcommands (e.g. `init`, `plan`, and `apply`)."
        ),
        "hook_point": "terraform_provision_cleanup",
        "module": "cbhooks/hookmodules/terraform/provision_cleanup.py",
        "enabled": True,
    },
    {
        "name": "Run Pre-Destroy Terraform",
        "description": (
            "Perform global setup logic before executing 'destructive' Terraform "
            "subcommands (e.g. `destroy`)."
        ),
        "hook_point": "terraform_pre_destroy",
        "module": "cbhooks/hookmodules/terraform/pre_destroy.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Destroy",
        "description": (
            "Defines the behavior that CloudBolt uses when calling the underlying "
            "`terraform destroy` command."
        ),
        "hook_point": "terraform_destroy",
        "module": "cbhooks/hookmodules/terraform/destroy.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Destroy Cleanup ",
        "description": (
            "Perform cleanup logic after `terraform destroy` "
            "regardless of success or failure."
        ),
        "hook_point": "terraform_destroy_cleanup",
        "module": "cbhooks/hookmodules/terraform/destroy_cleanup.py",
        "enabled": True,
    },
    {
        "name": "Run Terraform Destroy Failure ",
        "description": (
            "Perform cleanup logic after a failed 'destructive' Terraform "
            "subcommand (e.g. `terraform destroy`)."
        ),
        "hook_point": "terraform_destroy_failure",
        "module": "cbhooks/hookmodules/terraform/destroy_failure.py",
        "enabled": True,
    },
    {
        "name": "Run Post-Destroy Terraform",
        "description": (
            "Perform teardown and verification logic after executing 'destructive' "
            "Terraform subcommands (e.g. `destroy`)."
        ),
        "hook_point": "terraform_post_destroy",
        "module": "cbhooks/hookmodules/terraform/post_destroy.py",
        "enabled": True,
    },
    # Options for SSH Keys
    {
        "name": "Generate Options for SSH Keys",
        "description": (
            "Generates options for which SSH Keys can be associated with a Server "
        ),
        "hook_point": "generated_custom_field_options",
        "module": "cbhooks/hookmodules/generate_options_for_ssh_keys.py",
        "enabled": True,
        "custom_fields": ["key_name", "keypair_name"],
    },
]
# Additional hook
hooks.extend(alibaba_hooks)

# END HOOK-RELATED OBJECTS ###

rules = [
    {
        "name": "email_group_admins_when_quota_usage_exceeded",
        "label": "Email group admins when quota usage over threshold",
        "description": (
            "When the group quota's actual usage reaches a "
            "threshold, then send an email to the group admins."
        ),
        "condition": {
            "name": "Group quota usage exceeds threshold",
            "description": (
                "Look through each quota on each group to determine "
                "whether its actual usage is over defined threshold of the "
                "quota limit."
            ),
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/group_quota_over_threshold.py",
            "inputs": [
                {
                    "name": "threshold",
                    "label": _lazy("Threshold"),
                    "description": _lazy(
                        "A decimal value between 0 and 1, for the threshold percentage "
                        "group quotas should be checked against"
                    ),
                    "type": "DEC",
                    "namespace": "action_inputs",
                    "minimum": 0,
                    "maximum": 1,
                    "value_pattern_string": "{:.0%}",
                }
            ],
        },
        "action": {
            "name": "Email group admins quota usage warning",
            "description": (
                "Go through each specified group quota and email "
                "the admins of that group to notify them that "
                "the quota usage has exceeded a threshold."
            ),
            "enabled": False,
            "shared": False,
            "module": "cbhooks/hookmodules/rules/actions/group_quota_warning_email.py",
        },
        "mappings": {"threshold": 0.8},
    },
    {
        "name": "email_cb_admin_when_license_warnings",
        "label": "Email CB Admin when license warning for thresholds",
        "description": (
            "When the license is less than a threshold number "
            "of days from expiration or more than a threshold "
            "percentage of its maximum servers are in use, then "
            "send an email to the CB admin."
        ),
        "enabled": True,
        "condition": {
            "name": "License has warnings for thresholds",
            "description": (
                "Determine whether the license will expire in less "
                "than threshold days or has more than threshold "
                "percent of maximum servers in use."
            ),
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/license_warnings_for_thresholds.py",
            "inputs": [
                {
                    "name": "threshold_days_before_expires",
                    "label": "Threshold Number of Days Before Expiration",
                    "description": (
                        "The number of days where, if the license will "
                        "expire in less than that many days, a warning "
                        "should be raised"
                    ),
                    "type": "INT",
                    "namespace": "action_inputs",
                },
                {
                    "name": "threshold_percent_servers_used",
                    "label": "Threshold Percent of Servers Used",
                    "description": (
                        "The percent from 0-100 where, if the percentage "
                        "of the license's maximum possible servers being "
                        "used is greater than it, a warning "
                        "should be raised"
                    ),
                    "type": "INT",
                    "namespace": "action_inputs",
                    "minimum": 0,
                    "maximum": 100,
                    "value_pattern_string": "{0:.0f}%",
                },
            ],
        },
        "action": {
            "name": "Send Email",
            "description": (
                "Send an email with the recipient, subject, and "
                "body passed from the If condition."
            ),
            "enabled": True,
            "shared": False,
            "module": "cbhooks/hookmodules/rules/actions/send_email.py",
        },
        "mappings": {
            "threshold_days_before_expires": 30,
            "threshold_percent_servers_used": 75,
        },
    },
    {
        "name": "email_owners_aws_vms_missing_required_tags",
        "label": "Email owners of AWS VMs Missing Required Tags",
        "description": (
            "If there are any AWS instances missing one of the "
            "specified required tags, email their owners."
        ),
        "condition": {
            "name": "aws_vms_missing_required_tags",
            "description": (
                "If there are any AWS instances missing one of the "
                "specified required tags, add them to the list so "
                "they can have an action performed on them."
            ),
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/aws_without_required_tags.py",
            "inputs": [],
        },
        "action": {
            "name": "Email server owners for missing tags",
            "description": (
                "Determine the owner of each AWS instance missing at "
                "least one required tag, and email them a warning "
                "that includes which tags are missing"
            ),
            "enabled": False,
            "shared": False,
            "module": "cbhooks/hookmodules/rules/actions/aws_tags_warning_email.py",
        },
    },
    {
        "name": "notify_admins_when_a_newer_version_of_CloudBolt_is_available",
        "label": "Notify admins when a newer version of CloudBolt is available",
        "description": (
            "Checks what the latest general availability (GA) release of "
            "CloudBolt is and saves this version info in order to show an "
            "alert on the Admin page."
        ),
        "enabled": True,
        "condition": {
            "name": "Fetch latest CloudBolt release info",
            "description": 'Fetch latest version info from cloudbolt.io and pass it on to the "Then" action if it is newer than what is installed.',
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/fetch_latest_cb_version_info.py",
            "inputs": [],
        },
        "action": {
            "name": "Send Email",
            "description": (
                "If new, relevant releases are found, email the CB admin to let them know they "
                "are available."
            ),
            "enabled": True,
            "module": "cbhooks/hookmodules/rules/actions/send_email.py",
            "shared": True,
        },
    },
    {
        "name": "clean_up_old_snapshots",
        "label": "Clean up Old Snapshots",
        "description": (
            "Find and destroy old snapshots that may adversely affect performance."
        ),
        "condition": {
            "name": "Find Old VMware Snapshots",
            "description": ".",
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/find_old_snapshots.py",
            "inputs": [
                {
                    "name": "threshold_days",
                    "label": "Threshold Number of Days Before Expiration",
                    "description": (
                        "The number of days before this condition will flag the snapshots for "
                        "deletion"
                    ),
                    "type": "INT",
                    "namespace": "action_inputs",
                    "minimum": 0,
                },
                {
                    "name": "dry_run",
                    "label": "Dry Run",
                    "description": (
                        'When set to "True", this rule will identify the VMs that would be '
                        "deleted, but will not delete them."
                    ),
                    "type": "BOOL",
                    "namespace": "action_inputs",
                },
            ],
        },
        "action": {
            "name": "Delete Snapshots",
            "description": (""),
            "enabled": True,
            "module": "cbhooks/hookmodules/rules/actions/delete_snapshots.py",
            "shared": False,
        },
        "mappings": {"dry_run": True, "threshold_days": 30},
    },
    {
        "name": "fetch_and_cache_available_azure_images",
        "label": "Fetch and Cache Available Azure Images",
        "enabled": True,
        "description": (
            "Fetches images using a CloudBolt-provided whitelist by default. To add your own whitelist, "
            "add a list named AZURE_IMAGE_WHITELIST to your customer_settings.py file. "
            "If you wish to disable the whitelist and import all images, set the action input to False. "
            "Fetching the full list of available images from Azure API takes around 20 minutes per "
            "location. Doing this in an asynchronous rule/job lets the Import Images dialog "
            "load in seconds rather than minutes. Rules run nightly by default but may be run "
            "on-demand as well."
        ),
        "condition": {
            "name": "Find Azure resource handlers",
            "description": "Find all Azure resource handlers and pass to actions.",
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/find_azure_arm_resource_handlers.py",
        },
        "action": {
            "name": "Fetch and Cache available Azure images",
            "description": (
                "Fetches and caches image data for all Azure resource handlers passed from "
                "the condition, using a CloudBolt-provided whitelist by default. To add your own whitelist, "
                "add a list named AZURE_IMAGE_WHITELIST to your customer_settings.py file. "
                'If you wish to disable the whitelist and import all images, set the action input "use_whitelist" '
                "to False."
            ),
            "enabled": True,
            "module": "cbhooks/hookmodules/rules/actions/cache_available_Azure_ARM_images.py",
            "shared": False,
            "inputs": [
                {
                    "name": "use_whitelist",
                    "label": "Use whitelist",
                    "description": (
                        "A boolean action input for using a whitelist when running the 'Fetch and Cache Available "
                        "Images' rule. When set to True, the rule will look in customer_settings.py for a whitelist "
                        "of templates. If not found, we fall back to using a predefined whitelist."
                    ),
                    "type": "BOOL",
                    "namespace": "action_inputs",
                }
            ],
            "mappings": {"use_whitelist": False},
        },
    },
    {
        "name": "expire_resources",
        "label": "Expire Resources",
        "enabled": False,
        "description": (
            "Finds all deployed resources whose Expiration Date has "
            "passed and performs the configured actions to expire them."
        ),
        "condition": {
            "name": "Find Expired Resources",
            "description": (
                "Finds all deployed resources where their value for the "
                "Expiration Date parameter has passed."
            ),
            "shared": False,
            "module": "cbhooks/hookmodules/rules/conditions/find_expired_resources.py",
        },
        "action": {
            "name": "Send Email About or Delete Expired Resources",
            "description": (
                "Notifies resource owners that their resource has expired and "
                "potentially, if a resource has been expired for more than "
                "the threshold number of days, deletes the resource."
            ),
            "enabled": False,
            "module": "cbhooks/hookmodules/rules/actions/email_or_delete_expired_resources.py",
            "shared": False,
            "inputs": [
                {
                    "name": "threshold_days_expired",
                    "label": "Threshold Days Expired",
                    "description": (
                        "The threshold for how many days a resource should be "
                        "expired before it gets deleted."
                    ),
                    "type": "INT",
                    "namespace": "action_inputs",
                }
            ],
            "mappings": {"threshold_days_expired": 30},
        },
    },
]


all_blueprints = [
    {
        # This is the Blueprint linked to by New Server
        "any-group-can-deploy": True,
        "build-items": [
            {
                "all-environments-enabled": True,
                "deploy-seq": 1,
                "description": "",
                "enabled-environments": [],
                "execute-in-parallel": False,
                "hostname-template": "",
                "name": "Server",
                "show-on-order-form": True,
                "type": "provserver",
            }
        ],
        "description": "Provision a new server",
        "groups-that-can-deploy": [],
        "groups-that-can-manage": [],
        "icon": "initialize/blueprints/custom_server/icon.png",
        "name": "Custom Server",
        "management-actions": [],
        "teardown-items": [],
    }
]


portals = [{"name": "CloudBolt", "is_default": True}]

recurring_jobs = [
    {
        "name": "Refresh Server Rates",
        "enabled": True,
        "description": """
            Refresh rates by downloading the rate files for GCE and AWS.
        """,
        "type": "recurring_action",
        "hook_name": "Refresh Server Rates",
        "schedule": "45 3 * * 0",  # Every sunday at 3:45 AM
    },
    {
        "name": "Sync all Resource Handlers",
        "description": "Pull a complete inventory to discover new VMs, update existing ones ("
        "including power status, hardware, name, etc), and mark ones that no "
        "longer exist as historical.",
        "type": "syncvms",
        "param_class": SyncVMParameters,
        "schedule": "0,30 * * * *",
    },
    {
        "name": "Run all CIT Tests",
        "description": "Run all enabled continuous infrastructure tests. See Admin > CIT for "
        "more info.",
        "type": "functionaltest",
        "param_class": FunctionalTestParameters,
        "schedule": "0 2 * * *",
    },
    {
        "name": "Execute all Rules",
        "description": "Execute the condition for all enabled rules to ensure compliance in the "
        "environment. See Admin > Rules for more info.",
        "type": "runautomations",
        "param_class": TriggerParameters,
        "schedule": "0 1 * * *",
    },
    {
        "name": "Refresh All Server Utilization",
        "enabled": False,
        "description": """
            Execute any action whose name starts with "Refresh Utilization ". Updates server
            utilization stats used in reports. See sample action "Refresh Utilization for VMware
            Servers".
        """,
        "type": "recurring_action",
        "hook_name": "Refresh All Server Utilization",
        "schedule": "45 3 * * *",
    },
    {
        "name": "Clean RH Networks & Templates",
        "enabled": False,
        "description": """
            Clean up any networks or templates in CB that are no longer valid
            by syncing with what is on the Resource Handler.
        """,
        "type": "recurring_action",
        "hook_name": "Clean RH Networks & Templates",
        "schedule": "0 4 * * *",
    },
    {
        "name": "Update Search Index",
        "enabled": True,
        "description": """
            Refreshes the search index that enables the global search feature. Running this on a
            regular basis ensures that objects new to CloudBolt will show up in search results.

            The search index resides in /var/opt/cloudbolt/search_index/ and should only take a few
            minutes to update.
        """,
        "type": "recurring_action",
        "hook_name": "Update Search Index",
        # Every 12 minutes. It should take <2 minutes to complete.
        "schedule": "3,15,27,39,51 * * * *",
    },
    {
        "name": "Auto-power control servers",
        "enabled": False,
        "description": (
            "This recurring job enables auto-powering off of servers for periods of the day. This can be useful for "
            "servers that do not need to run at night, to save on public cloud costs/resource consumption at "
            "those times of the day. "
            "To use this feature, go to a server's details page and configure a power "
            "schedule on the tab or use the Power Schedule parameter at order time. "
            "When the action runs it will look for the ScheduledTime models "
            "created by you setting the power schedule, and use them to determine which "
            "servers should be powered on or off at the current time. "
            "CloudBolt will use its own server time to judge whether it is the right time to power on and "
            "off VMs, so make sure you know what time it is on the CB server and that the timezone is right. "
            "Also note that this recurring job is expected to be run "
            "every hour on the hour. If it is run on a different schedule, that will impact "
            "when servers are powered on or off. The power change will only happen if the job runs "
            "during the hour on the day when a power change is scheduled."
        ),
        "type": "recurring_action",
        "hook_name": "Auto-power control servers",
        # Once/hour at the beginning of the hour
        "schedule": "0 * * * *",
    },
    {
        "name": "Auto-power control resources",
        "enabled": False,
        "description": (
            "This recurring job enables auto-powering off of a resource's servers for periods of the day. "
            "This can be useful for multi-server applications where startup and shutdown order of "
            "servers is important. "
            "It uses the deploy sequence of server tiers originally set in the blueprint for a given resource to "
            "determine the order in which servers will power on or off. "
            "To use this feature, go to a resource's details page and configure a power "
            "schedule on the tab."
            "When the action runs it will look for the ScheduledTime models "
            "created by you setting the power schedule, and use them to determine which "
            "resources should have their servers powered on or off at the current time. "
            "CloudBolt will use its own server time to judge whether it is the right time to power on and "
            "off VMs, so make sure you know what time it is on the CB server and that the timezone is right. "
            "Also note that this recurring job is expected to be run "
            "every hour on the hour. If it is run on a different schedule, that will impact "
            "when servers are powered on or off. The power change will only happen if the job runs "
            "during the hour on the day when a power change is scheduled."
        ),
        "type": "recurring_action",
        "hook_name": "Auto-power control resources",
        # Once/hour at the beginning of the hour
        "schedule": "0 * * * *",
    },
    {
        "name": "Delete Old Job Records",
        "enabled": True,
        "description": (
            "Find any job record in the database older than the threshold "
            "and delete it, also removing its log file from disk."
        ),
        "type": "recurring_action",
        "hook_name": "Delete Old Job Records",
        # Once a day, at 2:15am
        "schedule": "15 2 * * *",
    },
    {
        "name": "Download Azure Resource Manager Invoice",
        "enabled": True,
        "description": "Download the latest monthly invoice for all Azure ARM Resource Handlers.",
        "type": "recurring_action",
        "hook_name": "Download Azure Resource Manager Invoice",
        # monthly at 2am on the first day of the month.
        "schedule": "0 2 1 * *",
    },
    {
        "name": "Download Azure rate card",
        "enabled": True,
        "description": "Download the latest rate card from Azure for all Azure ARM Resource Handlers.",
        "type": "recurring_action",
        "hook_name": "Download Azure rate card",
        # once a day at 1:15am
        "schedule": "15 1 * * *",
    },
    {
        "name": "Associate IPAM Networks",
        "enabled": False,
        "type": "recurring_action",
        "hook_name": "Associate IPAM Networks",
    },
    {
        "name": "Import Public Cloud Billing Data",
        "enabled": True,
        "type": "recurring_action",
        "description": "Download last month's billing data for the pub cloud providers and add "
        "any server-related costs to the CB DB.",
        "hook_name": "Import Public Cloud Billing Data",
        # monthly at 2am on the first day of the month.
        "schedule": "0 2 1 * *",
    },
    {
        "name": "Download Currency Exchange Rates",
        "enabled": False,
        "description": "Download the latest exchange rates for supported currencies.",
        "type": "recurring_action",
        "hook_name": "Download Currency Exchange Rates",
        # Daily at 2am.
        "schedule": "0 2 * * *",
    },
    {
        "name": "Sync Resources",
        "enabled": False,
        "description": (
            "For any Blueprint that has a Discovery Plug-in specified, "
            "use that logic to discover and sync Resources of the type "
            "described by that Blueprint."
        ),
        "type": "recurring_action",
        "hook_name": "Sync Resources",
        # Daily at 1:15am
        "schedule": "15 1 * * *",
    },
    {
        "name": "Refresh Blueprints from Remote Source",
        "enabled": False,
        "description": (
            "For any Blueprint that is configured to be populated from a definition "
            "stored in a remote source location, refresh that Blueprint using the "
            "Remote Source URL that is set on it. This is an automated alternative "
            "to using the manual refresh button on each such Blueprint."
        ),
        "type": "recurring_action",
        "hook_name": "Refresh Blueprints from Remote Source",
        # Daily at 3:15am
        "schedule": "15 3 * * *",
    },
    {
        "name": "Sync CloudBolt Order Status with ServiceNow Catalog Request Status",
        "enabled": False,
        "description": (
            "Get list of current pending orders and check the status"
            'in ServiceNow. If status has changed to "approved" or "rejected",'
            "change CB order status accordingly."
        ),
        "type": "recurring_action",
        "hook_name": "Sync CloudBolt Order Status with ServiceNow Catalog Request Status",
        # Every 15 minutes
        "schedule": "*/15 * * * *",
    },
    {
        "name": "Content Library Caching",
        "enabled": True,
        "description": "Create local cached files for per-collection, CloudBolt hosted content",
        "type": "recurring_action",
        "hook_name": "Content Library Caching",
        # once a day at 12:05am
        "schedule": "5 0 * * *",
    },
]

all_dataprotection_technologies = [
    {
        "name": "Cohesity",
        "modulename": "dataprotection.cohesity.models.CohesityDataProtection",
    },
    {
        "name": "Rubrik",
        "modulename": "dataprotection.rubrik.models.RubrikDataProtection",
    },
    {
        "name": "Azure Backup",
        "modulename": "dataprotection.azure_backup.models.AzureBackupDataProtection",
    },
    {
        "name": "CommVault",
        "modulename": "dataprotection.commvault.models.CommVaultDataProtection",
    },
]


tenant_permissions = [
    {
        "name": "resourcehandler.manage",
        "label": "Manage Resource Handlers",
        "description": "Manage everything about resource handlers",
    },
    {
        "name": "configmanager.manage",
        "label": "Manage Configuration Managers",
        "description": "Manage everything about Configuration Managers",
    },
    {
        "name": "osbuild.manage",
        "label": "Manage OS Builds",
        "description": "Manage everything about OS Builds",
    },
    {
        "name": "application.manage",
        "label": "Manage Applications",
        "description": "Manage everything about Applications",
    },
    {
        "name": "network.manage",
        "label": "Manage Networks",
        "description": "Manage everything about Networks",
    },
    {
        "name": "ipam.manage",
        "label": "Manage IPAMs",
        "description": "Manage everything about IPAMs",
    },
    {
        "name": "preconfiguration.manage",
        "label": "Manage Preconfigurations",
        "description": "Manage everything about Preconfigurations",
    },
    {
        "name": "sshkey.manage",
        "label": "Manage SSH Keys",
        "description": "Manage everything about SSH Keys",
    },
    {
        "name": "environment.manage",
        "label": "Manage Environments",
        "description": "Manage everything about Environments",
    },
    {
        "name": "containerorchestrator.manage",
        "label": "Manage Container Orchestrators",
        "description": "Manage everything about Container Orchestrators",
    },
    {
        "name": "user.manage",
        "label": "Manage Users",
        "description": "Manage everything about Users",
    },
    {
        "name": "resourcepool.manage",
        "label": "Manage Resource Pools",
        "description": "Manage everything about Resource Pools",
    },
]


tenant_roles = [
    {
        "label": "Tenant Admin",
        "name": "tenant_admin",
        "description": "By default, grants all administrative permissions.",
        "permissions": ["*"],
    },
]


# For Haystack search results that allow navigating somewhere by search term
# The `description` value may reuse our existing spotlight keywords
# (data-spotlight attribute on links in the Admin). Note the name is already
# searchable, so you don't need to add words in the name to the description
#
# Note: You must run create_objects.py and kick off the 'Update Search Index'
# recurring job in order to see new entries.
COMMON_ACTION_KEYWORDS = "scripts flows hooks orchestrate orchestration plugins plug-ins webhooks action automate executable code"
static_pages = [
    dict(name="Admin Home", url="/admin/", description="CloudBolt administration"),
    dict(name="Dashboard", url="/dashboard/", description="home dash reports"),
    dict(name="Servers", url="/servers/", description=""),
    dict(name="Catalog", url="/catalog/", description="blueprints order"),
    dict(name="Reports", url="/reports/", description="charts graphs jasper"),
    dict(
        name="Groups",
        url="/groups/",
        description="group organizations teams membership",
    ),
    dict(name="Environments", url="/environments/", description=""),
    dict(
        name="Resource Handlers",
        url="/admin/resourcehandlers/",
        description=(
            "aws govcloud amazon azure microsoft gce google ipmi kvm qemu openstack "
            "helion hp hpcloud verizon vcenter vsphere "
            "vmware xen"
        ),
    ),
    dict(name="Networks", url="/networks/", description="vlan router routing nic"),
    dict(
        name="Network Virtualization",
        url="/network_virtualization/",
        description="nsxt",
    ),
    dict(
        name="CloudBolt Resource Pools",
        url="/resourcepools/",
        description="ip address collections",
    ),
    dict(name="Provisioning Engines", url="/provengines/", description="razor",),
    dict(
        name="Configuration Managers",
        url="/providers/",
        description="chef docker puppet ansible",
    ),
    dict(name="IP Management", url="/ipam/", description="infoblox bigip dns"),
    dict(
        name="Container Orchestrators",
        url="/containerorchestrators/",
        description="docker kubernetes",
    ),
    dict(name="ITSM", url="/itsm/", description="itsm servicenow"),
    dict(
        name="OS Builds",
        url="/externalcontent/osbuilds/",
        description="operating system windows linux template image ami",
    ),
    dict(
        name="Parameters",
        url="/admin/customfields/",
        description="order param CF field defaults",
    ),
    dict(
        name="Preconfigurations",
        url="/admin/preconfigs/",
        description="order param bundle CF field",
    ),
    dict(
        name="Jobs",
        url="/jobs/",
        description="sync provision decom expire expiration cron",
    ),
    dict(name="Job Statistics", url="/jobs/stats_list/", description="jobs"),
    dict(
        name="History",
        url="/admin/history/",
        description="history events table list overview combined",
    ),
    dict(
        name="Recurring Jobs",
        url="/recurring_jobs/",
        description="cron scheduled jobs nightly periodic",
    ),
    dict(
        name="Continuous Infrastructure Testing (CIT)", url="/cit/", description="tests"
    ),
    dict(name="Users", url="/users/", description="profile"),
    dict(
        name="Roles",
        url="/roles/",
        description="requestor approver viewer perm permission admin",
    ),
    dict(name="Permissions", url="/permissions/", description="perm"),
    dict(
        name="CloudBolt Portals",
        url="/portals/",
        description="multitenant custom branding",
    ),
    dict(
        name="LDAP Authentication Settings",
        url="/admin/ldap_settings/",
        description="sso single sign-on active directory ad",
    ),
    dict(name="Email Settings", url="/admin/email_settings/", description="smtp mail"),
    dict(name="Rates", url="/rates_admin/", description="chargeback cost expense"),
    dict(
        name="Miscellaneous Settings",
        url="/admin/misc_settings/",
        description=(
            "proxy home homepage help security misc console social facebook twitter linkedin avatar recipient"
        ),
    ),
    dict(name="All Actions", url="/actions/", description=COMMON_ACTION_KEYWORDS),
    dict(
        name="Server Actions",
        url="/actions/server_actions/",
        description=COMMON_ACTION_KEYWORDS,
    ),
    dict(
        name="Resource Actions",
        url="/actions/resource_actions/",
        description=COMMON_ACTION_KEYWORDS + "deployed",
    ),
    dict(
        name="Rules",
        url="/actions/rules/",
        description=COMMON_ACTION_KEYWORDS
        + "trigger event if then point condition cron",
    ),
    dict(
        name="Orchestration Actions",
        url="/actions/orchestration_actions/",
        description=COMMON_ACTION_KEYWORDS + "trigger point jobs orders",
    ),
    dict(
        name="External Orchestrators",
        url="/orchestrators/",
        description="action flow hpoo vco orchestration engine",
    ),
    dict(
        name="UI Extensions",
        url="/extensions/manage_extensions/",
        description="tabs reports dashboard customize xui",
    ),
    dict(name="API Browser", url="/api/", description=""),
    dict(
        name="CloudBolt Release Information",
        url="/admin/version_detail/",
        description="version build upgrade alpha rc ga",
    ),
    dict(
        name="Resource Types",
        url="/resource_types/",
        description="resources types xaas orders",
    ),
    dict(
        name="Catalog Management",
        url="/catalog/manage",
        description="blueprints labels categories categorization taxonomy organization",
    ),
    dict(
        name="System Status",
        url="/admin/status/",
        description="system status service job engine maintenance",
    ),
    dict(
        name="Security Information and Event Management (SIEM) Providers",
        url="/siem/",
        description="log logging notification monitoring",
    ),
    dict(
        name="Multi-Channel Alerts",
        url="/alerts/",
        description="channels email slack security alert",
    ),
    dict(
        name="Single Sign-On", url="/authentication/saml2/", description="sso saml2 idp"
    ),
]


def run_external_create_routines():
    """
    Run the create minimal routines specified by other applications.
    """
    from connectors.objects import create_minimal

    create_minimal()

    from behavior_mapping.models import initialize_sequenced_items

    # This only creates the initial set of sequences if none exist already.
    # Prevents destruction during upgrading of a CB with existing sequences.
    initialize_sequenced_items(reset=False)

    # starting in 9.5 EULA for CLoudBolt will be using the EULA model instead of being implicit in
    # the QuickSetup execution
    from product_license.eula.services import EULAService

    EULAService.create()
