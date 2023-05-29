#!/usr/bin/env python
from __future__ import print_function
import json

import sys

from externalcontent.models import OSFamily
from infrastructure.models import Server  # noqa: F841, F401
from jobengine.jobmodules.syncvmsjob import ServerUpdater
from jobs.models import Job
from resourcehandlers.ipmi.models import IPMIResourceHandler
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)

if __name__ == "__main__":
    import django

    django.setup()


remote_script = r"""#!/usr/bin/env python

import socket
import json
import glob
import re
import os


def get_cpu_cnt():
    # cribbed from http://echorand.me/site/notes/articles/python_linux/article.html
    cpuinfo = {}
    procinfo = {}

    nprocs = 0
    with open('/proc/cpuinfo') as f:
        for line in f:
            if not line.strip():
                # end of one processor
                cpuinfo['proc%s' % nprocs] = procinfo
                nprocs = nprocs + 1
                # Reset
                procinfo = {}
            else:
                if len(line.split(':')) == 2:
                    procinfo[line.split(':')[0].strip()] = line.split(':')[1].strip()
                else:
                    procinfo[line.split(':')[0].strip()] = ''
    return nprocs


def get_mem_size():
    ''' Return total amount of memory as a decimal'''
    meminfo = {}
    if not os.path.exists('/proc/meminfo'):
        return None
    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()
    mem_kb, _ = meminfo['MemTotal'].split()
    mem_gb = int(mem_kb) / (1024.0 * 1024.0)
    return mem_gb


def size(device):
    nr_sectors = open(device+'/size').read()
    sect_size = open(device+'/queue/hw_sector_size').read()
    if not sect_size or not nr_sectors:
        return None
    if '\n' in sect_size:
        sect_size = sect_size.rstrip('\n')
    if '\n' in nr_sectors:
        nr_sectors = nr_sectors.rstrip('\n')

    # The sect_size is in bytes, so we convert it to GiB and then send it back
    return (float(nr_sectors)*float(sect_size))/(1024.0*1024.0*1024.0)


def detect_disks():
    '''
    Return a two-tuple: (list of disk info, total disk size)
    '''
    # Add any other device pattern to read from
    dev_pattern = ['sd.*',]
    disks = []
    total_disk_size = 0
    for device in glob.glob('/sys/block/*'):
        for pattern in dev_pattern:
            if re.compile(pattern).match(os.path.basename(device)):
                disk_size = size(device)
                disks.append({'name': device, 'uuid': device, 'disk_size': disk_size})
                total_disk_size += disk_size
    return disks, int(total_disk_size)


# Cribbed from http://stackoverflow.com/questions/270745/how-do-i-determine-all-of-my-ip-addresses-when-i-have-multiple-nics
def get_nics():
    try:
        import netifaces
    except:
        return []
    index = 1
    nic_list = []
    for interface in netifaces.interfaces():
        if interface in ['lo']:
            continue
        for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
            nic_list.append({
                'index': index,
                'ip_address': link['addr'],
                'mac': netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr'],
                'network': None,
            })
            index += 1
    return nic_list


def get_os_family():
    try:
        import platform
    except:
        return None
    platform.linux_distribution()[0]


info_dict = {}
info_dict['hostname'] = socket.gethostname()
info_dict['os_family'] = get_os_family()
info_dict['cpu_cnt'] = get_cpu_cnt()
info_dict['mem_size'] = get_mem_size()
info_dict['nics'] = get_nics()
info_dict['disks'], info_dict['disk_size'] = detect_disks()
print json.dumps(info_dict)
"""


def run(job, **kwargs):
    """
    Note: this depends on Python 2.6+ being on the remote machine
    """
    rh = IPMIResourceHandler.objects.first()

    for server in job.server_set.all():
        vm_dict_out = server.execute_script(script_contents=remote_script).strip()
        vm_dict = json.loads(vm_dict_out)
        logger.debug("Fetched vm_dict: {}".format(vm_dict))
        if vm_dict:
            osf = vm_dict.get("os_family")
            if osf:
                vm_dict["os_family"] = OSFamily.objects.get(name=osf)
            vm_dict["power_status"] = "POWERON"
            updater = ServerUpdater(server, vm_dict, created=False, rh=rh)
            updater.update()
            server.save()

        return "SUCCESS", "", ""


if __name__ == "__main__":
    # Useful for testing purposes
    print(run(job=Job.objects.get(id=sys.argv[1]),))
