from common.methods import set_progress
from cbhooks.models import CloudBoltHook
from django.utils.html import format_html
from resourcehandlers.models import ResourceHandler
from infrastructure.models import Environment

from utilities.templatetags.helper_tags import render_simple_link
from utilities.logger import ThreadLogger

import boto3

logger = ThreadLogger("AWSSgForm_Save")
# https://stackoverflow.com/questions/70824745/update-security-group-tags-using-boto3
# https://gist.github.com/miztiik/3cc85c8d01b25e21ad7168eeea32e96c


def resolve_ipProtocol(ipProtocol):
    if ipProtocol == -1:
        ipProtocol = 'all'
    if ipProtocol == 1:
        ipProtocol = 'tcp'
    elif ipProtocol == 2:
        ipProtocol = 'udp'
    elif ipProtocol == 3:
        ipProtocol = 'icmp'
    elif ipProtocol == 'tcp':
        ipProtocol = 1
    elif ipProtocol == 'udp':
        ipProtocol = 2
    elif ipProtocol == 'cmp':
        ipProtocol = 3
    else:
        ipProtocol = 'Unknown'

    return ipProtocol

def create_new_aws_sg(security_group_name,
                  security_group_desc,
                  direction,
                  vpcid,
                  ip_protocol,
                  from_port,
                  to_port,
                  cidr_ip,
                  region,
                  env_id):
    logger.info(f"Creating AWS Security Group {security_group_name},  {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()

    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        response = ec2_client.create_security_group(GroupName=security_group_name,
                                                    Description=security_group_desc,
                                                    VpcId=vpcid)
        security_group_id = response['GroupId']
        
        if direction == 'Ingress':
            data = ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': ip_protocol,
                     'FromPort': int(from_port),
                     'ToPort': int(to_port),
                     'IpRanges': [{'CidrIp': cidr_ip}]}
                ])
            logger.info('Ingress Successfully Set ')
            return True, "The AWS Security group was created"
        elif direction == 'Egress':
            data = ec2_client.authorize_security_group_egress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': ip_protocol,
                     'FromPort': int(from_port),
                     'ToPort': int(to_port),
                     'IpRanges': [{'CidrIp': cidr_ip}]}
                ])
            logger.info("Egress Successfully Set ")
            return True, "The AWS Security group was created"
    except Exception as e:
        return False, f"The security group could not be created. Reason: {e}"
        
def delete_aws_sg(group_id, group_name, env_id):
    logger.info(f"Deleting AWS Security Group {group_name}, {group_id}, {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    logger.info(f"Deleting SG from {region}")
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        ec2_client.delete_security_group(GroupId=group_id)
        return True, "AWS Security Group Successfully Deleted"
    except Exception as e:
                           
        return False, f"AWS Security Group Failed to Delete {e}"
    
def create_aws_sg_inbound(group_id, 
                          inbr_name,
                          inbr_protocol,
                          inbr_from_port,
                          inbr_to_port,
                          inbr_cidr,
                          inbr_desc, 
                          env_id):
    
    if str(inbr_protocol) == '1':
        inbr_protocol = 'tcp'
    elif str(inbr_protocol) == '2':
        inbr_protocol = 'udp'
    elif str(inbr_protocol) == '3':
        inbr_protocol = 'icmp'
    else:
        inbr_protocol = 'Unknown'    
    
    logger.info(f"Creating AWS Security Group Inbound Rule {inbr_name}, {inbr_protocol}, {inbr_to_port}, {inbr_cidr}, {inbr_desc}, {group_id}, {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    #logger.info(f"Creating AWS SG Inbound Rule  for {region}")
    # uses EC2 Client with authorize_security_group_ingress
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        
        auth_ingress_res = ec2_client.authorize_security_group_ingress(GroupId=group_id,
                                                      IpPermissions=
                                                      [{
                                                          'IpProtocol': f'{inbr_protocol}',
                                                          'FromPort': int(inbr_from_port),
                                                          'ToPort': int(inbr_to_port),
                                                          'IpRanges':
                                                              [
                                                                  {
                                                                      'CidrIp': f'{inbr_cidr}',
                                                                      'Description': f'{inbr_desc}'
                                                                      }
                                                                  ]
                                                              },
                                                       ]
                                                      )
        #logger.info(f"auth_ingress_res = {auth_ingress_res}")
        
        return True, "AWS Security Group Inbound Rule Successfully Created"
    except Exception as e:
                           
        return False, f"AWS Security Group Inbound Rule Failed to Create {e}"

def delete_aws_sg_inbound(env_id, igresscnt, ipProtocol, fromPort, toPort):
    if str(ipProtocol) == '1':
        ipProtocol = 'tcp'
    elif str(ipProtocol) == '2':
        ipProtocol = 'udp'
    elif str(ipProtocol) == '3':
        ipProtocol = 'icmp'
    else:
        ipProtocol = 'Unknown'
        
    logger.info(f"Deleting AWS Security Group Inbound Rule {igresscnt}, {env_id}, {ipProtocol},  {fromPort}, {toPort} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    # logger.info(f"Deleting SG Inbound Rule {fromPort}  to {toPort} from {igresscnt}")      
    revoke_res = ''
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        grpc = 1
        ec2secgr = ec2_client.describe_security_groups()
        
        targetigresscnt = igresscnt 
        targetipProtocol = ipProtocol.lower() 
        targetfromPort = fromPort 
        targettoPort = toPort 


        group_id = ''
        group_name = ''
        vpcId = ''

        igressrulecnt = 0
        cntb = 1
        cntc = 1
        cnt = 1
        
        for e in ec2secgr["SecurityGroups"]:
            group_id = e["GroupId"]
            group_name = e["GroupName"]
            vpcId = e["VpcId"]
            
            if(len(e["IpPermissions"]) > 1):
                    for permission in e["IpPermissions"]:
                         
                        igressrulecnt = igressrulecnt + 1
                        
                        if "FromPort" not in permission:
                            currIpPermission = permission["IpProtocol"].lower()
                            logger.info(f"1) {currIpPermission} From Port missing")
                           
                        else:
                            currIpPermission = permission["IpProtocol"].lower()
                            ipP = permission["IpProtocol"].lower()
                            frP = permission["FromPort"]
                            toP = permission["ToPort"]
                            cidr_ip = permission["IpRanges"][0]["CidrIp"] 
                            if "Description" in permission["IpRanges"][0]:
                                cidr_desc= permission["IpRanges"][0]["Description"]
                            else:
                                cidr_desc = ''
                            userIdgrpPairs = dict()    
                            revoke_perm = [{
                                        "FromPort": int(frP),
                                        "IpProtocol": "{ipP}".format(ipP=ipP),
                                        "ToPort": int(toP),
                                        "IpRanges": [
                                                    {
                                                    "CidrIp": "{cidr_ip}".format(cidr_ip=cidr_ip),
                                                    "Description": "{cidr_desc}".format(cidr_desc=cidr_desc)
                                                    },
                                                    ],
                                        "UserIdGroupPairs": [
                                                            {
                                                            "GroupId": "{group_id}".format(group_id=group_id),
                                                            "VpcId": "{vpcId}".format(vpcId=vpcId)
                                                            },
                                                            ]
                                            }]
 
                            #logger.info(f"revoke_perm = {revoke_perm}")
                            #logger.info(f"3) {targetigresscnt} vs {igressrulecnt} {targetipProtocol} vs {ipP} and  {targetfromPort} vs {frP} {targettoPort} vs {toP} ")
                            if str(targetigresscnt) == str(igressrulecnt) and str(targetipProtocol) == str(ipP) and str(targetfromPort) == str(frP) and str(targettoPort) == str(toP):
                                #logger.info(f"3b) revoking {group_id} {revoke_perm}")
                                revoke_res = ec2_client.revoke_security_group_ingress(GroupId=group_id,IpPermissions=revoke_perm,DryRun=False)
                                if revoke_res['Return'] ==True:
                                    return True, f"AWS Security Group Inbound Rule Successfully Deleted from {group_id}"
                                else:
                                    return False, f"AWS Security Group Inbound Rule Failed to Delete {revoke_res}"
                        # logger.info(f"5) {targetigresscnt} vs igressrulecnt = {igressrulecnt}")    
            else:
                    igressrulecnt = igressrulecnt + 1
                    permission = e["IpPermissions"][0]
                    currIpPermission = permission["IpProtocol"].lower()
                    ipP = e["IpProtocol"].lower()
                    frP = e["FromPort"]
                    toP = e["ToPort"]
                    cidr_ip = permission["IpRanges"][0]["CidrIp"]
                    if "Description" in permission["IpRanges"][0]:
                        cidr_desc= permission["IpRanges"][0]["Description"]
                    else:
                        cidr_desc = ''  
                    revoke_perm = [{
                                        "FromPort": int(frP),
                                        "IpProtocol": "{ipP}".format(ipP=ipP),
                                        "ToPort": int(toP),
                                        "IpRanges": [
                                                    {
                                                    "CidrIp": "{cidr_ip}".format(cidr_ip=cidr_ip),
                                                    "Description": "{cidr_desc}".format(cidr_desc=cidr_desc)
                                                    },
                                                    ],
                                        "UserIdGroupPairs": [
                                                            {
                                                            "GroupId": "{group_id}".format(group_id=group_id),
                                                            "VpcId": "{vpcId}".format(vpcId=vpcId)
                                                            },
                                                            ]
                                            }]
                    #logger.info(f"4) {currIpPermission} vs {ipP} and {targetigresscnt} vs {igressrulecnt} {targetfromPort} vs {frP} {targettoPort} vs {toP}")
                    if str(targetigresscnt) == str(igressrulecnt) and str(targetipProtocol) == str(ipP) and str(targetfromPort) == str(frP) and str(targettoPort) == str(toP):              
                        revoke_res = ec2_client.revoke_security_group_ingress(GroupId=group_id,IpPermissions=revoke_perm,DryRun=False)
                        if revoke_res['Return'] ==True:
                            return True, f"AWS Security Group Inbound Rule Successfully Deleted from {group_id}"
                        else:
                            return False, f"AWS Security Group Inbound Rule Failed to Delete {revoke_res}"
    
    except Exception as e:
                           
        return False, f"AWS Security Group Inbound Rule Failed to Delete {e}"

def create_aws_sg_outbound(group_id, 
                          outbr_name,
                          outbr_protocol,
                          outbr_from_port,
                          outbr_to_port,
                          outbr_cidr,
                          outbr_desc, 
                          env_id):
    logger.info(f"outbound rule {outbr_protocol}")
    if str(outbr_protocol) == '1':
        outbr_protocol = 'tcp'
    elif str(outbr_protocol) == '2':
        outbr_protocol = 'udp'
    elif str(outbr_protocol) == '3':
        outbr_protocol = 'icmp'
    else:
        outbr_protocol = 'Unknown' 
    
    logger.info(f"Creating AWS Security Group outbound Rule {outbr_name}, {outbr_protocol}, {outbr_cidr}, {group_id}, {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    #logger.info(f"Creating AWS SG outbound Rule  for {region}")
    # uses EC2 Client with authorize_security_group_ingress
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        
        ec2_client.authorize_security_group_egress(GroupId=group_id,
                                                      IpPermissions=
                                                      [{
                                                          'IpProtocol': f'{outbr_protocol}',
                                                          'FromPort': int(outbr_from_port),
                                                          'ToPort': int(outbr_to_port),
                                                          'IpRanges':
                                                              [
                                                                  {
                                                                      'CidrIp': f'{outbr_cidr}',
                                                                      'Description': f'{outbr_desc}'
                                                                      }
                                                                  ]
                                                              },
                                                       ]
                                                      )
        return True, "AWS Security Group outbound Rule Successfully Created"
    except Exception as e:
                           
        return False, f"AWS Security Group outbound Rule Failed to Create {e}"
 

def delete_aws_sg_outbound(env_id, egresscnt, ipProtocol, fromPort):
    if str(ipProtocol) == '0':
        ipProtocol = 'all'
    if str(ipProtocol) == '1':
        ipProtocol = 'tcp'
    elif str(ipProtocol) == '2':
        ipProtocol = 'udp'
    elif str(ipProtocol) == '3':
        ipProtocol = 'icmp'
    else:
        ipProtocol = 'Unknown'
        
    logger.info(f"Deleting AWS Security Group Outbound Rule {egresscnt}, {env_id}, {ipProtocol},  {fromPort} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    #logger.info(f"Deleting SG Outbound Rule Port {fromPort} from {egresscnt}")      
    revoke_res = ''
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        grpc = 1
        ec2secgr = ec2_client.describe_security_groups()
        
        targetegresscnt = egresscnt 
        targetipProtocol = ipProtocol.lower() 
        targetfromPort = fromPort 
       
        group_id = ''
        group_name = ''
        vpcId = ''

        egressrulecnt = 0
        cntb = 1
        cntc = 1
        cnt = 1
        
        for e in ec2secgr["SecurityGroups"]:
            group_id = e["GroupId"]
            group_name = e["GroupName"]
            vpcId = e["VpcId"]
            
            if(len(e["IpPermissionsEgress"]) > 1):
                    for permission in e["IpPermissionsEgress"]:
                         
                        egressrulecnt = egressrulecnt + 1
                        logger.info(f"1) permission= {permission}")
                        if "FromPort" not in permission:
                            currIpPermission = permission["IpProtocol"].lower()
                            logger.info(f"1) {currIpPermission} From Port missing")
                           
                        else:
                            currIpPermission = permission["IpProtocol"].lower()
                            ipP = permission["IpProtocol"].lower()
                            frP = permission["FromPort"]
                            cidr_ip = permission["IpRanges"][0]["CidrIp"] 
                            if "Description" in permission["IpRanges"][0]:
                                cidr_desc= permission["IpRanges"][0]["Description"]
                            else:
                                cidr_desc = ''
                            userIdgrpPairs = dict()    
                            revoke_perm = [{
                                        "FromPort": frP,
                                        "ToPort": frP,
                                        "IpProtocol": "{ipP}".format(ipP=ipP),
                                        "IpRanges": [
                                                    {
                                                    "CidrIp": "{cidr_ip}".format(cidr_ip=cidr_ip),
                                                    "Description": "{cidr_desc}".format(cidr_desc=cidr_desc)
                                                    },
                                                    ],
                                        "UserIdGroupPairs": [
                                                            {
                                                            "GroupId": "{group_id}".format(group_id=group_id),
                                                            "VpcId": "{vpcId}".format(vpcId=vpcId)
                                                            },
                                                            ]
                                            }]
 
                            #logger.info(f"revoke_perm = {revoke_perm}")
                            #logger.info(f"3) {targetegresscnt} vs {egressrulecnt} {targetipProtocol} vs {ipP} and  {targetfromPort} vs {frP} ")
                            if str(targetegresscnt) == str(egressrulecnt) and str(targetipProtocol) == str(ipP) and str(targetfromPort) == str(frP):
                                #logger.info(f"3b) revoking {group_id} {revoke_perm}")
                                revoke_res = ec2_client.revoke_security_group_egress(GroupId=group_id,IpPermissions=revoke_perm,DryRun=False)
                                if revoke_res['Return'] ==True:
                                    return True, f"AWS Security Group Outbound Rule Successfully Deleted from {group_id}"
                                else:
                                    return False, f"AWS Security Group Outbound Rule Failed to Delete {revoke_res}"
                        # logger.info(f"5) {targetigresscnt} vs igressrulecnt = {igressrulecnt}")    
            else:
                    permission = e["IpPermissions"][0]
                    logger.info(f"1a) permission= {permission}")
                    egressrulecnt = egressrulecnt + 1
                    currIpPermission = permission["IpProtocol"].lower()
                    ipP = permission["IpProtocol"].lower()
                    frP = permission["FromPort"]
                    cidr_ip = permission["IpRanges"][0]["CidrIp"]
                    if "Description" in permission["IpRanges"][0]:
                        cidr_desc= permission["IpRanges"][0]["Description"]
                    else:
                        cidr_desc = ''  
                    revoke_perm = [{
                                        "FromPort": frP,
                                        "ToPort": frP,
                                        "IpProtocol": "{ipP}".format(ipP=ipP),
                                        "IpRanges": [
                                                    {
                                                    "CidrIp": "{cidr_ip}".format(cidr_ip=cidr_ip),
                                                    "Description": "{cidr_desc}".format(cidr_desc=cidr_desc)
                                                    },
                                                    ],
                                        "UserIdGroupPairs": [
                                                            {
                                                            "GroupId": "{group_id}".format(group_id=group_id),
                                                            "VpcId": "{vpcId}".format(vpcId=vpcId)
                                                            },
                                                            ]
                                            }]
                    logger.info(f"4) {currIpPermission} vs {ipP} and {targetegresscnt} vs {egressrulecnt} {targetfromPort} vs {frP}")
                    if str(targetegresscnt) == str(egressrulecnt) and str(targetipProtocol) == str(ipP) and str(targetfromPort) == str(frP):              
                        revoke_res = ec2_client.revoke_security_groupegress(GroupId=group_id,IpPermissions=revoke_perm,DryRun=False)
                        if revoke_res['Return'] ==True:
                            return True, f"AWS Security Group Outbound Rule Successfully Deleted from {group_id}"
                        else:
                            return False, f"AWS Security Group Outbound Rule Failed to Delete {revoke_res}"
    
    except Exception as e:
                           
        return False, f"AWS Security Group Outbound Rule Failed to Delete {e}"

    
def create_aws_sg_tag(group_id, tag_key, tag_value, env_id):
    logger.info(f"Creating AWS Security Group  Tag {tag_key}, {tag_value}, {group_id}, {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    #logger.info(f"Creating AWS SG Tag for {region}")
    try:
        ec2_resource = boto3.resource('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        security_group = ec2_resource.SecurityGroup(group_id)
        security_group.create_tags(Tags=[{'Key': tag_key,'Value': tag_value},])
    
        return True, "AWS Security Group Tag Successfully Created"
    except Exception as e:
                           
        return False, f"AWS Security Group Tag Failed to Create {e}"
    
def delete_aws_sg_tag(env_id, group_id, tag_key):
    logger.info(f"Deleting AWS Security Group Tag {group_id}, {env_id} ")
    env = Environment.objects.get(id=env_id)
    rh = env.resource_handler.cast()
    region = env.aws_region
    logger.info(f"Deleting SG Tag {tag_key} from {group_id}")      
    
    try:
        ec2_client = boto3.client('ec2',
                     region_name=region,
                     aws_access_key_id=rh.serviceaccount,
                     aws_secret_access_key=rh.servicepasswd
                    )
        ec2secgr = ec2_client.describe_security_groups()
        # tag_key will be the number of the tag in the list
        # get the value
        cnt = 1
        key_to_lookup = "Tags"
        for tags in ec2secgr["SecurityGroups"]:
            cntc = 1
            if key_to_lookup in tags:
                if tags["GroupId"] == group_id:
                    for t in tags["Tags"]:
                        logger.info(f"{t}")
                        if str(cnt) == str(tag_key):
                            # replace the number in the list with the value
                            actual_tag_key = t["Key"]
                            resdel = ec2_client.delete_tags(Resources=[group_id], Tags=[{'Key': actual_tag_key}])
                            logger.info(f"{resdel}")
                            if resdel["ResponseMetadata"]["HTTPStatusCode"] == 200:
                                return True, f"AWS Security Group Tag {actual_tag_key} Successfully Deleted from {group_id}"
                            else:
                                return False, f"AWS Security Group Tag Failed to Delete {resdel}"
                        cnt = cnt + 1
        
    
    except Exception as e:
                           
        return False, f"AWS Security Group Tag Failed to Delete {e}"