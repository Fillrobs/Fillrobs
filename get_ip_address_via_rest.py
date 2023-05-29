"""
Get API Via REST
"""
from utilities.models import ConnectionInfo
import json
import requests

from common.methods import set_progress

def get_ip_address(refNo):
    
    ci = ConnectionInfo.objects.get(name='APITest')
    url = f"{ci.protocol}://{ci.ip}:{ci.port}/reservation-service/api/reservations/index.php?reqno={refNo}"
    response = requests.get(url)
 
    jstr = response.content.decode("UTF-8")
    jsonstr = json.loads(jstr)
    ipaddress = jsonstr['ipaddress']
  
    
    return ipaddress


def generate_options_for_pr_ref_no(**kwargs):
    """Generate a drop down list of pr_ref_no

    Returns:
        dropdown: list
    """
    options = ["------",'1','2','3', '4', '5', '6', '7']
    
    return options


def run(job, **kwargs):
    set_progress("This will show up in the job details page in the CB UI, and in the job log")

    refNo = '{{ pr_ref_no }}'

    ipaddress = get_ip_address(refNo)

    return "SUCCESS", "Sample output message", ""
    