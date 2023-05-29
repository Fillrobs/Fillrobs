export class LoaderClass {
  constructor(tagName) {
    this.tagName = tagName;
  }
  
  display() { 
    $(`${this.tagName} .loader`).addClass('in'); 
    $(`${this.tagName} .loader.fade.in`).css({
      "width": `${$(`#${this.tagName}`).width()}px`, 
      "height": `${$(`#${this.tagName}`).height()}px`, 
      "top": `${$(`#${this.tagName}`).position().top}px`, 
      "bottom": 'none', 
      "left": `${$(`#${this.tagName}`).position().left}px`, 
      "right": 'none', 
    });
  }

  hide() { $(`${this.tagName} .loader`).removeClass('in'); }

}

export var DATA_BACKUP_HOURS = 6;

export async function fetchViaPost(url, rh_id, csrfToken) {
  const response = await fetch(url, {
    body: JSON.stringify({ "rh_id": rh_id }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    method: "post"
  });
  return await response.json();
};

export function numberFormatter(number) {
  if (Number.isFinite(number)) {
    number = (!Number.isInteger(number)) ? number.toFixed(2) : number;
    var parts = number.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
  } else {
    return 0;
  }
  
}

export const AWS_SERVICE_TYPE_MATCH = {
  'Services::Compute::Server::Volume': { name: 'Detached Volumes', id: 'volume' },
  'Services::Compute::Server': {
    name: 'Legacy Instance Sizing(EC2)',
    id: 'instances_sizing'
  },
  'Services::Database::Rds': {
    name: 'Legacy Instance Sizing(RDS)',
    id: 'rds_instances_sizing'
  },
  'ec2_right_sizings': {
    name: 'Right Sizing(EC2)',
    id: 'ec2_right_sizings'
  },
  // 'Services::Compute::ECS::Cluster':{ name: 'Volume Snapshots', id: 'volume_snapshot' },
  'AwsRecords::Snapshots::Volume': { name: 'Volume Snapshots', id: 'volume_snapshot' },
  'AwsRecords::Snapshots::Rds': { name: 'RDS Snapshots', id: 'rds_snapshot' },
  'Services::Network::ElasticIP': { name: 'Unassociated Elastic IPs', id: 'elastic_ip' },
  'Services::Network::AutoScalingConfiguration': { name: 'Unused Launch Configurations', id: 'launch_config' },
  'amis': { name: 'AMI', id: 'amis' },
  'Services::Network::LoadBalancer': { name: 'Load Balancers in Unhealthy State', id: 'load_balancer' },
  'idle_ec2': { name: 'Idle Running Services(EC2)', id: 'idle_ec2' },
  'idle_rds': { name: 'Idle Running Services(RDS)', id: 'idle_rds' },
  'idle_stopped_ec2': { name: 'Idle Stopped Services(EC2)', id: 'idle_stopped_ec2' },
  'idle_stopped_rds': { name: 'Idle Stopped Services(RDS)', id: 'idle_stopped_rds' },
  'idle_volume': { name: 'Idle Running Services(Volume)', id: 'idle_volume' },
  'idle_load_balancer': { name: 'Idle Running Services(LoadBalancer)', id: 'idle_load_balancer' },
  'unused_provisioned_iops_volumes': { name: 'Unused provisioned IOPS (Volume)', id: 'unused_provisioned_iops_volumes' },
  'unused_provisioned_iops_rds': { name: 'Unused provisioned IOPS (RDS)', id: 'unused_provisioned_iops_rds' },
  'ignore_services': { name: 'Ignored Services', id: 'ignore_services' }
}

export const AWS_SERVICE_TAG_MAP = {
  "rds_snapshot": "Snapshots::AWS",
  "volume_snapshot": "Snapshots::AWS",
  "volume": "Services::Compute::Server::Volume::AWS",
  "elastic_ip": "Services::Network::ElasticIP::AWS",
  "launch_config": "Services::Network::AutoScalingConfiguration::AWS",
  "amis": "MachineImage",
  "load_balancer": "Services::Network::LoadBalancer::AWS",
  "instances_sizing": "Services::Compute::Server::AWS",
  "rds_instances_sizing": "Services::Database::Rds::AWS",
  "unused_provisioned_iops_volumes": "ProvisionedIops",
  "unused_provisioned_iops_rds": "ProvisionedIops",
  "ec2_right_sizings": "Ec2RightSizing",
  "idle_load_balancer": "idle_load_balancer",
  "idle_volume": "idle_volume",
  "idle_stopped_rds": "idle_stopped_rds",
  "idle_stopped_ec2": "idle_stopped_ec2",
  "idle_rds": "idle_rds",
  "idle_ec2": "idle_ec2",
  "ignore_services": "ignore_services"
}

export const AZURE_SERVICE_TYPE_MATCH = {
  'idle_vm': { name: 'Idle VM (Running)', id: 'idle_vm' },
  'idle_stopped_vm': { name: 'Idle VM (Stopped)', id: 'idle_stopped_vm' },
  'idle_databases': { name: 'Idle Databases', id: 'idle_databases' },
  'idle_disks': { name: 'Idle Disks', id: 'idle_disks' },
  'idle_lbs': { name: 'Idle Load Balancers', id: 'idle_lbs' },
  'unassociated_lbs': { name: 'Unassociated Load Balancers', id: 'unassociated_lbs' },
  'unassociated_public_ips': { name: 'Unassociated Public IPs', id: 'unassociated_public_ips' },
  'unattached_disks': { name: 'Unattached Disks', id: 'unattached_disks' },
  'unused_snapshots': { name: 'Unused Snapshots', id: 'unused_snapshots' },
}

export const AZURE_SERVICE_TAG_MAP = {
  "idle_vm": "idle_vm",
  "idle_stopped_vm": "idle_stopped_vm",
  "idle_databases": "idle_databases",
  "idle_disks": "idle_disks",
  "idle_lbs": "idle_lbs",
  "unassociated_lbs": "unassociated_lbs",
  "unassociated_public_ips": "get_unassociated_public_ips",
  "unattached_disks": "unattached_disks",
  "unused_snapshots": "unused_snapshots"
}

export const SERVICE_WISE_METRICS = {
  "idle_vm": ["Percentage Cpu", "Network In Total", "Network Out Total", 
              "OS Disk Read Operations/Sec", "OS Disk Write Operations/Sec", 
              "VM Cached IOPS Consumed Percentage"],
  "idle_stopped_vm": ["Percentage Cpu", "Network In Total", "Network Out Total", 
                      "OS Disk Read Operations/Sec", "OS Disk Write Operations/Sec", 
                      "VM Cached IOPS Consumed Percentage"],
  "idle_databases": {
    "PostgreSQL" : ["network_bytes_ingress", "network_bytes_egress", "io_consumption_percent"],
    "MariaDB" : ["network_bytes_ingress", "network_bytes_egress", "io_consumption_percent"],
    "MySQL" : ["network_bytes_ingress", "network_bytes_egress", "io_consumption_percent"],
    "SQL" : ["dtu_consumption_percent"],
  },
  "idle_disks": ["Composite Disk Read Bytes/sec",
                 "Composite Disk Write Bytes/sec",
                 "Composite Disk Read Operations/sec",
                 "Composite Disk Write Operations/sec"],
  "idle_lbs": ["ByteCount"],
  "ec2_right_sizings": ["CPUUtilization", "DiskReadBytes",
                        "DiskReadOps", "DiskWriteBytes", "DiskWriteOps",
                        "NetworkIn", "NetworkOut", "NetworkPacketsIn",
                        "NetworkPacketsOut", "MemoryUtilization"],
  "idle_load_balancer": ["RequestCount"],
  "idle_volume": ["VolumeReadOps", "VolumeWriteOps"],
  "idle_stopped_rds": ["DatabaseConnections", "WriteIOPS", "ReadIOPS"],
  "idle_stopped_ec2": ["CPUUtilization", "NetworkIn", "NetworkOut",
                       "NetworkPacketsIn", "NetworkPacketsOut",
                       "MemoryUtilization"],
  "idle_rds": ["DatabaseConnections", "WriteIOPS", "ReadIOPS"],
  "idle_ec2": ["CPUUtilization", "NetworkIn", "NetworkOut",
               "NetworkPacketsIn", "NetworkPacketsOut", 
               "MemoryUtilization"],
  'unused_provisioned_iops_volumes': ["VolumeReadOps", "VolumeWriteOps"],
  'unused_provisioned_iops_rds': ["DatabaseConnections", "WriteIOPS", "ReadIOPS"],
}

export const PROP_MAPPING = {
  "image_id": "Image ID",
  "instance_id": "Instance ID",
  "instance_type": "Instance type",
  "volume_id": "Volume ID",
  "lifecycle": "Lifecycle",
  "VolumeType": "Type",
  "volume_type": "Type",
  "volume_size": "Size",
  "VolumeSize": "Size",
  "encrypted": "Encrypted",
  "port": "Port",
  "owner_id": "Owner",
  "iops": "IOPS",
  "engine": "Engine",
  "snapshot_type": "Type",
  "engine_version": "Version",
  "allocated_storage": "Storage",
  "block_device_mappings": "Block Device",
  "architecture": "Architecture",
  "platform": "Platform",
  "status": "Status",
  "virtualization_type": "Virtualization Type",
  "scheme": "Scheme",
  "unused_instance_count": "Unused Instance Count",
  "unused_instance_description": "Unused Instance Description",
  "root_device_type": "Root Device Type",
  "block_device_mapping": "Block Device Mapping",
  "state": "State",
  "storage_size": "Storage Size",
  'instance_type': 'Instance type',
  'platform': 'Platform',
  'tier': 'Tier',
  'family': 'Family',
  'capacity': 'Capacity',
  'size': 'Size',
  'provisioned_IOPS': 'Provisioned IOPS',
  'type': 'Type',
  'sku': 'Sku',
  'allocation': 'Allocation',
  'version': 'version',
  'disk_size_gb': 'Disk Size GB',
  'source_disk': 'Source Disk'
};

export const AWS_COLUMN_TO_SHOW = [
  { title: "Name" }, 
  { title: "Region" }, 
  { title: "Additional Properties" }, 
  { title: "Service Tags" }, 
  { title: "MEC" }, 
  { title: "Days Old" }, 
  { title:"", 'className':'details-control','orderable': false, 'data': '', 'defaultContent': '<i class="fas fa-angle-down fa-2x"></i>' }
]

export const AWS_COLUMN_TO_SHOW_1 = [
  { title: "Name" }, 
  { title: "Region" }, 
  { title: "Lifecycle" }, 
  { title: "Additional Properties" }, 
  { title: "Service Tags" }, 
  { title: "MEC" }, 
  { title: "Days Old" }, 
  { title: "", 'className': 'details-control', 'orderable': false, 'data': '', 
    'defaultContent': '<i class="fas fa-angle-down fa-2x"></i>' }]

export const AZURE_COLUMN_TO_SHOW = [
  { title: "Service Name(ID)" }, 
  { title: "Region" }, 
  { title: "State" }, 
  { title: "Additional Properties" }, 
  { title: "Service Tags" }, 
  { title: "MEC" }, 
  { title: "Days Old" }, 
  { title:"", 'className':'details-control','orderable': false, 'data': '', 'defaultContent': '<i class="fas fa--down fa-2x"></i>' }
]

export const DIMENSION_DATA = {
  "AWS": {
    "custom_type":{
      "overview": "date",
      "service": "service",
      "region": "region",
      "tags": "tag_aws:createdBy",
      "usage_type": "date",
      "purchase_option": "date",
    },
    "compute_type":{
      "overview": "date",
      "region": "region",
      "tags": "tag_aws:createdBy",
      "usage_type": "date",
      "instance_type": "instance_size",
    },
    "database_type":{
      "overview": "date",
      "database_engine": "db_engine",
      "tags": "tag_aws:createdBy",
      "sub_services": "service",
      "instance_type": "instance_size",
    },
    "storage_type":{
      "overview": "date",
      "region": "region",
      "tags": "tag_aws:createdBy",
      "bucket": "date",
      "sub_services": "service",
    },
    "data_transfer_type":{
      "overview": "date",
      "region": "region",
      "tags": "tag_aws:createdBy",
      "sub_services": "service",
      "bucket": "date",
      "source": "date",
    },
  },
  "Azure": {
    "custom_type":{
      "overview": "date",
      "resource_group": "resource_group",
      "location": "location",
      "service_name": "service_name",
    },
    "other_type":{
      "overview": "date",
      "resource_group": "resource_group",
      "location": "location",
      "service_tier": "service_tier",
    },
  }
}

export const AWS_SERVICE_MAP = {
  "AWS Budgets": "",
  "AWS CloudShell": "",
  "AWS CloudTrail": "",
  "AWS CodeArtifact": "",
  "AWS Config": "",
  "AWS Cost Explorer": "",
  "AWS Data Pipeline": "",
  "AWS Data Transfer": "",
  "AWS Elemental MediaStore": "",
  "AWS Glue": "",
  "AWS Key Management Service": "(KMS)",
  "AWS Lambda": "",
  "AWS Secrets Manager": "",
  "AWS Security Hub": "",
  "AWS Service Catalog": "",
  "AWS Step Functions": "",
  "AWS Support (Business)": "",
  "AWS Systems Manager": "",
  "AWS WAF": "",
  "AWS X-Ray": "",
  "Accelario Oracle Database Migration": "",
  "Amazon API Gateway": "",
  "Amazon Athena": "",
  "Amazon CloudFront": "", 
  "Amazon DynamoDB": "(DDB)",
  "Amazon EC2 Container Registry (ECR)": "",
  "Amazon EC2 Container Service": "(ECS)",
  "Amazon Elastic Compute Cloud": "(EC2)",
  "Amazon Elastic Container Service for Kubernetes": "(EKS)",
  "Amazon Elastic File System": "(EFS)",
  "Amazon Lightsail":"",
  "Amazon Redshift": "",
  "Amazon Rekognition": "",
  "Amazon Relational Database Service": "(RDS)",
  "Amazon Route 53": "",
  "Amazon SageMaker": "",
  "Amazon Simple Email Service": "(SES)", 
  "Amazon Simple Notification Service": "(SNS)",
  "Amazon Simple Queue Service": "(SQS)",
  "Amazon Simple Storage Service": "(S3)",
  "Amazon Transcribe": "",
  "AmazonCloudWatch": "",
  "Elastic Load Balancing": "(ELB)",
  "Kumolus - Cloud Management SaaS": "",
  "Savings Plans for AWS Compute usage": "",
}

export const MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
"July", "August", "September", "October", "November", "December"
];

export const SERVER_PARTS = {
  "ips": "IP",
  "instance_type": "Instance Type",
  "amis": "AMI",
  "backup": "Backup",
  "storage": "Storage",
  "data_transfer": "Data Transfer"
}

export const POTENTIAL_SAVINGS = {
  "Currently Idle": "Currently Idle EC2",
  "Idle Running Volume": "Idle Running Volume",
  "AMI": "AMI",
  "Volume Snapshots": "Volume Snapshots",
  "Right Sizing (EC2)": "Right Sizing (EC2)",
  "Legacy Instance Sizing (EC2)": "Legacy Instance Sizing (EC2)",
  "Currently Idle VM": "Currently Idle VM",
  "Idle Disks": "Idle Disks",
  "Unused Snapshots": "Unused Snapshots",
  "Right Sizing (VM)": "Right Sizing (VM)"
}