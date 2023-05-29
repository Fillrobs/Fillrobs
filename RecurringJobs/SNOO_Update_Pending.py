import sys
import json

import requests

from django.contrib.auth.models import User
from common.methods import set_progress
from orders.models import Order, get_current_time, ActionJobOrderItem
#from utilities.servicenow_api import ServiceNowAPI
from utilities.logger import ThreadLogger
from utilities.models import ConnectionInfo
from utilities.exceptions import CloudBoltException
from django.utils.html import escape, format_html
from jobs.models import Job
from django.utils.translation import ugettext as _

logger = ThreadLogger("SNOO Sync")

"""
SNOO Service Request Queue
~~~~~~~~~~~~~~~~~~~~~~~~~
Syncs CloudBolt Order Approval status with SNOO Approval status.
Based off of unique id sent to SNOO when Order is submitted.

Version Req.
~~~~~~~~~~~~
CloudBolt 9.0
"""

#########################
### Settings Override ###

### Status Options ###
"""
Response field from SNOO.
'stage', 'request_state', 'approval' are options often used.
'approval' is default setting
'order_approve' and 'order_deny' are CloudBolt specific and required.
Example: status_levels = {'order_approve':{'approval': ['approved']},'order_deny':{'approval': ['rejected']}}
"""

### SNOOw Approval Status Field ###
"""
set_approval_field()
Default is 'approval'
Example: ServiceNowAPI().set_approval_field('stage')
"""
def request_snoo(data, conn, url, logger=None):
    """
    Make REST call and return the response
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    #response = requests.post(
    #    url=url,
    #    data=data,
    #    auth=(conn.username, conn.password),
    #    headers=headers
    #)
    response = requests.get(
        url=url,
        auth=(conn.username, conn.password),
        headers=headers
    )
    if response.status_code != 200:
        err = (
            'Failed to Get SNOO Record, response from '
            'SNOO:\n{}'.format(response.content)
              )
        return err
    else :    
        logger.info('Response from SNOO:\n{}'.format(response.content))
        return response.content


def get_snoo_status(cmp_order_id):
    conn = ConnectionInfo.objects.get(name='localhost_mysql')
    
    snoo_url = "{}://{}:{}".format(conn.protocol, conn.ip, conn.port)

    url = snoo_url + "/readorder.php?cmp_order_id={cmp_order_id}".format(cmp_order_id=cmp_order_id)
    response = request_snoo("NULL", conn, url, logger=logger)

    return_data = response.decode('utf-8')
    return_data_json = json.loads(return_data)
    return return_data_json

def get_approver():
    approver, created = User.objects.get_or_create(
        email="probins-ext@cloudbolt.io",
        defaults={"username": "cloudbolt",
                  "first_name": "cloud",
                  "last_name": "bolt"})
    return approver


def run(job=None, logger=None, **kwargs):

    set_progress("Running SNOO ticket queue manager")

    # Get all PENDING orders
    pending_orders = Order.objects.filter(status="PENDING")

    
    # If there are any pending orders, begin calling ServiceNow for the corresponding order item
    if pending_orders:

        #servicenow = ServiceNowAPI()

        # Override CloudBolt ServiceNow status checks here
        # servicenow.set_status_option(status_levels=status_levels)
        # servicenow.set_approval_field('approval')

        """
        Loop through pending orders which have a PENDING status.
        Update status to be the status which has been set in ServiceNow
        """
        for order in pending_orders:
            # Here we get the first order item as this is the one we're using to get the Pending Status attribute
            
            # ignore deletions that need approvals
            if hasattr(order, 'orderitem_set') == True: 
                order_item = order.orderitem_set.first()
                set_progress(f"order_item = {order_item}")
                if hasattr(order_item, 'blueprintorderitem') == True:
                    bp_order_item = order_item.blueprintorderitem
                    # update order status. Default to pending.
                    #status_message = servicenow.update_order_status(bp_order_item)
                    cmp_order_id = order.id
                    getOrderStatus = get_snoo_status(cmp_order_id)
                
                    set_progress(f"getOrderStatus {getOrderStatus} {len(getOrderStatus)}")
                    if len(getOrderStatus) > 0:
                        for p in getOrderStatus:
                            curr_db_status = p["order_status"]
                    else:
                        curr_db_status = 'NULL'


                    set_progress(f"Order Id {cmp_order_id} getOrderStatus {curr_db_status}")
                
                    logger.info(f"Order Id {cmp_order_id} and status = {curr_db_status}")
                    if curr_db_status == 'APPROVED':
                        approver = get_approver()
                        profile = approver.userprofile
                        order.approved_by = profile
                        order.approved_by_id = profile.id
                        order.approve_date = get_current_time()
                        order.status = 'ACTIVE'
                        order.save()
                        order.add_event("APPROVED", f"The '{order}' has been approved through SNoo by: USERID 2",profile=profile)
                        parent_job = None

                        # Saving job objects will cause them to be kicked off by the
                        # job engine within a minute
                        jobs = []
                        order_items = [oi.cast() for oi in order.orderitem_set.filter()]
                        for order_item in order_items:
                            jobtype = getattr(order_item, "job_type", None)
                            if not jobtype:
                                # the job type will default to the first word of the class type
                                # ex. "provision", "decom"

                                jobtype = str(order_item.real_type).split(" ", 1)[0]
                            quantity = 1

                            # quantity is a special field on order_items.  If an
                            # order_item has the quantity field, kick off that many
                            # jobs
                            if (
                                hasattr(order_item, "quantity")
                                and order_item.quantity is not None
                                and order_item.quantity != ""
                            ):
                                quantity = int(order_item.quantity)
                            for i in range(quantity):
                                job = Job(
                                    job_parameters=order_item,
                                    type=jobtype,
                                    owner=order.owner,
                                    parent_job=parent_job,
                                )
                                job.save()
                                if isinstance(order_item, ActionJobOrderItem):
                                    if order_item.server:
                                        servers = [order_item.server]
                                else:
                                    servers = []
                                    if hasattr(order_item, "server"):
                                        servers = [order_item.server]
                                    elif hasattr(order_item, "servers"):
                                        servers = order_item.servers.all()
                                    for server in servers:
                                        server.jobs.add(job)

                                jobs.append(job)

                        # If it didn't make any jobs, just call it done
                        if not jobs:
                            order.complete("SUCCESS")

                        msg = 'order complete'
                        set_progress(f"&nbsp;&nbsp;&nbsp;&nbsp;Order approved: {order.id}")


                    set_progress(f"Order Id {cmp_order_id} and status = {curr_db_status}")

    return "SUCCESS", "", ""