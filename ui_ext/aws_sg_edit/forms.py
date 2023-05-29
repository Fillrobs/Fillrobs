from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy as _lazy
from django.contrib import messages

from common.fields import form_field_for_cf
from common.forms import C2Form
from infrastructure.models import CustomField
from orders.models import CustomFieldValue
from utilities.logger import ThreadLogger
from xui.aws_sg_edit.methods import (create_new_aws_sg,
                                     delete_aws_sg,
                                     create_aws_sg_inbound,
                                     delete_aws_sg_inbound,
                                     create_aws_sg_outbound,
                                     delete_aws_sg_outbound,
                                     create_aws_sg_tag,
                                     delete_aws_sg_tag,)
from crispy_forms.helper import FormHelper

logger = ThreadLogger(__name__)
# https://boto3.amazonaws.com/v1/documentation/api/1.17.29/guide/ec2-example-security-group.html

class AWSCreateNewSgForm(C2Form):
     def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
     helper = FormHelper()
     myattrs = {'style': 'width:60%'}
     helper.label_class = "control-label col-lg-4"
     helper.field_class = "controls col-lg-8"
     direction_Choices = [
                      ('Ingress', 'Ingress'),
                      ('Egress', 'Egress')
                      ]
     IpProtocol_Choices = [
                      ('tcp', 'tcp'),
                      ('udp', 'udp'),
                      ('udp', 'icmp')
                      ]
     security_group_name = forms.CharField(label=_("SG Name"),
                           required=True,
                           max_length=100,
                           min_length=1,
                           )
     security_group_desc = forms.CharField(label=_("SG Description"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            )
     vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
     region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            ) 
     direction = forms.CharField(label=_("Direction"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.Select(choices=direction_Choices)
                            )
     ip_protocol = forms.CharField(label=_("IP Protocol"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.Select(choices=IpProtocol_Choices)
                            )
     from_port = forms.CharField(label=_("From Port"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            )
     to_port = forms.CharField(label=_("To Port"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            )
     cidr_ip = forms.CharField(label=_("CIDR IP"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            )
     env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
     perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
     
     def save(self):
         #logger.info(f"self={self}")
         security_group_name = self.cleaned_data['security_group_name']
         security_group_desc = self.cleaned_data['security_group_desc']
         direction = self.cleaned_data['direction']
         vpcid = self.cleaned_data['vpcid']
         ip_protocol  = self.cleaned_data['ip_protocol']
         from_port = self.cleaned_data['from_port']
         to_port = self.cleaned_data['to_port']
         cidr_ip = self.cleaned_data['cidr_ip']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         #logger.info("perform_action={perform_action}")
         try:
            if perform_action == 'create_new_aws_sg': 
                msg = create_new_aws_sg(
                            security_group_name,
                            security_group_desc,
                            direction,
                            vpcid,
                            ip_protocol,
                            from_port,
                            to_port,
                            cidr_ip,
                            region,
                            env_id
                )
            
            logger.info(f"msg={msg}")
            if msg[0] == False:
                return False, msg[1]
            else:
                return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg

class AWSDeleteSgForm(C2Form):
     def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
     helper = FormHelper()
     myattrs = {'style': 'width:60%'}
     helper.label_class = "control-label col-lg-3"
     helper.field_class = "controls col-lg-9"
     group_id = forms.CharField(label=_("Group ID"),
                           required=True,
                           max_length=260,
                           min_length=1,
                           widget=forms.TextInput(attrs={'readonly': 'readonly'})
                           )
     group_name = forms.CharField(label=_("Group Name"),
                           required=True,
                           max_length=260,
                           min_length=1,
                           widget=forms.TextInput(attrs={'readonly': 'readonly'})
                           )
     group_desc = forms.CharField(label=_("Group Description"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
     vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
     region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
     env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
     perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=10,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
     
     def save(self):
         # logger.info(f"self={self}")
         group_name = self.cleaned_data['group_name']
         group_desc = self.cleaned_data['group_desc']
         group_id = self.cleaned_data['group_id']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         
         try:
            if perform_action == 'delete': 
                msg = delete_aws_sg(
                            group_id,
                            group_name,
                            env_id
                )
            
            #logger.info(f"msg={msg}")
            if msg[0] == False:
                return False, msg[1]
            else:
                return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg
         
         
class AWSCreateSgInboundForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    IpProtocol_Choices = [
                      (1, 'tcp'),
                      (2, 'udp'),
                      (3, 'icmp')
                      ]

    
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    inbr_name = forms.CharField(label=_("Name"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        )
    inbr_protocol = forms.CharField(label=_("Protocol"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            widget=forms.Select(choices=IpProtocol_Choices)
                            )
    inbr_from_port = forms.CharField(label=_("From Port"),
                            required=True,
                            max_length=10,
                            min_length=1,
                            )
    inbr_to_port = forms.CharField(label=_("To Port"),
                            required=True,
                            max_length=10,
                            min_length=1,
                            )
    inbr_cidr = forms.CharField(label=_("Cidr"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            )
    inbr_desc = forms.CharField(label=_("Description"),
                            required=False,
                            max_length=512,
                            min_length=1,
                            )
    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
      
    def save(self):
         logger.info(f"self={self}")
         inbr_name = self.cleaned_data['inbr_name']
         inbr_protocol = self.cleaned_data['inbr_protocol']
         inbr_from_port = self.cleaned_data['inbr_from_port']
         inbr_to_port = self.cleaned_data['inbr_to_port']
         inbr_cidr = self.cleaned_data['inbr_cidr']
         inbr_desc = self.cleaned_data['inbr_desc']
         group_id = self.cleaned_data['group_id']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         #logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'create_aws_sg_inbound': 
                msg = create_aws_sg_inbound(
                            group_id,
                            inbr_name,
                            inbr_protocol,
                            inbr_from_port,
                            inbr_to_port,
                            inbr_cidr,
                            inbr_desc,
                            env_id
                )
            
            #logger.info(f"msg={msg}")
            if msg[0] == False:
                return False, msg[1]
            else:
                return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg
         
class AWSDeleteSgInboundForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    igresscnt = forms.CharField(label=_("igresscnt"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    ipProtocol = forms.CharField(label=_("ipProtocol"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    fromPort = forms.CharField(label=_("From Port"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    toPort = forms.CharField(label=_("To Port"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
      
    def save(self):
         #logger.info(f"self={self}")
         group_id = self.cleaned_data['group_id']
         igresscnt = self.cleaned_data['igresscnt']
         ipProtocol = self.cleaned_data['ipProtocol']
         fromPort = self.cleaned_data['fromPort']
         toPort = self.cleaned_data['toPort']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         #logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'delete_aws_sg_inbound': 
                msg = delete_aws_sg_inbound(
                            env_id,
                            igresscnt,
                            ipProtocol,
                            fromPort,
                            toPort
                )
            
                logger.info(f"msg={msg}")
                if msg[0] == False:
                    return False, msg[1]
                else:
                    return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg         
         
class AWSCreateSgOutboundForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    IpProtocol_Choices = [
                      (1, 'tcp'),
                      (2, 'udp'),
                      (3, 'icmp')
                      ]
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    outbr_name = forms.CharField(label=_("Name"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        )
    outbr_protocol = forms.CharField(label=_("Protocol"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            widget=forms.Select(choices=IpProtocol_Choices)
                            )
    outbr_from_port = forms.CharField(label=_("From Port"),
                            required=True,
                            max_length=10,
                            min_length=1,
                            )
    outbr_to_port = forms.CharField(label=_("To Port"),
                            required=True,
                            max_length=10,
                            min_length=1,
                            )
    outbr_cidr = forms.CharField(label=_("Cidr"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            )
    outbr_desc = forms.CharField(label=_("Description"),
                            required=False,
                            max_length=512,
                            min_length=1,
                            )
    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
      
    def save(self):
         # logger.info(f"self={self}")
         outbr_name = self.cleaned_data['outbr_name']
         outbr_protocol = self.cleaned_data['outbr_protocol']
         outbr_from_port = self.cleaned_data['outbr_from_port']
         outbr_to_port = self.cleaned_data['outbr_to_port']
         outbr_cidr = self.cleaned_data['outbr_cidr']
         outbr_desc = self.cleaned_data['outbr_desc']
         group_id = self.cleaned_data['group_id']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         #logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'create_aws_sg_outbound': 
                msg = create_aws_sg_outbound(
                            group_id,
                            outbr_name,
                            outbr_protocol,
                            outbr_from_port,
                            outbr_to_port,
                            outbr_cidr,
                            outbr_desc,
                            env_id
                )
            
            logger.info(f"msg={msg}")
            if msg[0] == False:
                return False, msg[1]
            else:
                return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg
         
class AWSDeleteSgOutboundForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    egresscnt = forms.CharField(label=_("egresscnt"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    ipProtocol = forms.CharField(label=_("ipProtocol"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    fromPort = forms.CharField(label=_("From Port"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )

    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )

    def save(self):
         #logger.info(f"self={self}")
         group_id = self.cleaned_data['group_id']
         egresscnt = self.cleaned_data['egresscnt']
         ipProtocol = self.cleaned_data['ipProtocol']
         fromPort = self.cleaned_data['fromPort']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         #logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'delete_aws_sg_outbound': 
                msg = delete_aws_sg_outbound(
                            env_id,
                            egresscnt,
                            ipProtocol,
                            fromPort
                )

                logger.info(f"msg={msg}")
                if msg[0] == False:
                    return False, msg[1]
                else:
                    return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg   
     
                  
class AWSCreateSgTagForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    tag_key = forms.CharField(label=_("Key"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        )
    tag_value = forms.CharField(label=_("Value"),
                            required=True,
                            max_length=512,
                            min_length=1,
                            )
    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
      
    def save(self):
         logger.info(f"self={self}")
         tag_key = self.cleaned_data['tag_key']
         tag_value = self.cleaned_data['tag_value']
         group_id = self.cleaned_data['group_id']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'create_aws_sg_tag': 
                msg = create_aws_sg_tag(
                            group_id,
                            tag_key,
                            tag_value,
                            env_id
                )
            
            logger.info(f"msg={msg}")
            if msg[0] == False:
                return False, msg[1]
            else:
                return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg
         
class AWSDeleteSgTagForm(C2Form):
    def __init__(self, *args, **kwargs):
           self.request = kwargs.pop('request', None)
                               
           super().__init__(*args, **kwargs)
           
    helper = FormHelper()
    myattrs = {'style': 'width:60%'}
    helper.label_class = "control-label col-lg-3"
    helper.field_class = "controls col-lg-9"
    group_id = forms.CharField(label=_("Group ID"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    tag_key = forms.CharField(label=_("Key"),
                        required=True,
                        max_length=260,
                        min_length=1,
                        widget=forms.TextInput(attrs={'readonly': 'readonly'})
                        )
    vpcid = forms.CharField(label=_("VpcId"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            #widget=forms.TextInput(attrs={'readonly': 'readonly'})
                            )
    region = forms.CharField(label=_("Region"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            ) 
    env_id = forms.CharField(label=_("env_id"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
    perform_action = forms.CharField(label=_("perform_action"),
                            required=True,
                            max_length=100,
                            min_length=1,
                            widget=forms.HiddenInput()
                            )
      
    def save(self):
         logger.info(f"self={self}")
         tag_key = self.cleaned_data['tag_key']
         group_id = self.cleaned_data['group_id']
         vpcid = self.cleaned_data['vpcid']
         region = self.cleaned_data['region']
         env_id = self.cleaned_data['env_id']
         perform_action = self.cleaned_data['perform_action']
         logger.info(f"perform_action={perform_action}")
         try:
            if perform_action == 'delete_aws_sg_tag': 
                msg = delete_aws_sg_tag(
                            env_id,
                            group_id,
                            tag_key
                            
                )
            
                logger.info(f"msg={msg}")
                if msg[0] == False:
                    return False, msg[1]
                else:
                    return True, msg[1]
         except Exception as e:
             logger.error(f"failed to process the form {e}")
             msg = _("Exception error: {e}")    
             return False, msg         