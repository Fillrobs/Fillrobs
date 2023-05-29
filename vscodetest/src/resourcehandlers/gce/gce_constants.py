# modify this list to change the images shown in the list when importing images
# for the handler. Note that we use the root-level image and not the images that
# are available from GCE: e.g. we provide centos-7 instead of centos-7-20160204;
# this is because the images available from GCE are deprecated or upgraded
# periodically and this would break your Templates.
# This list is based on: https://cloud.google.com/compute/docs/operating-systems/
from __future__ import unicode_literals

# "name" must be the name of the OS family in GCE!
# We look up the newest image for the OS family at deploy time.
common_images = [
    {"name": "centos-6", "guest_os": "CentOS 6", "total_disk_size": 10},
    {"name": "centos-7", "guest_os": "CentOS 7", "total_disk_size": 10},
    {"name": "debian-8", "guest_os": "Debian 8", "total_disk_size": 10},
    {"name": "debian-9", "guest_os": "Debian 9", "total_disk_size": 10},
    {"name": "rhel-6", "guest_os": "RedHat Enterprise 6", "total_disk_size": 10},
    {"name": "rhel-7", "guest_os": "RedHat Enterprise 7", "total_disk_size": 10},
    {"name": "sles-11", "guest_os": "SuSE Linux 11", "total_disk_size": 8},
    {"name": "sles-12", "guest_os": "SuSE Linux 12", "total_disk_size": 8},
    {"name": "opensuse-13", "guest_os": "openSUSE", "total_disk_size": 8},
    {"name": "ubuntu-1404-lts", "guest_os": "Ubuntu 1404", "total_disk_size": 10},
    {"name": "ubuntu-1604-lts", "guest_os": "Ubuntu 1604", "total_disk_size": 10},
    {"name": "ubuntu-1710", "guest_os": "Ubuntu 1710", "total_disk_size": 10},
    {
        "name": "windows-2008-r2",
        "guest_os": "Windows Server 2008 R2",
        "total_disk_size": 50,
    },
    {
        "name": "windows-2012-r2",
        "guest_os": "Windows Server 2012 R2",
        "total_disk_size": 50,
    },
    {"name": "windows-2016", "guest_os": "Windows Server 2016", "total_disk_size": 50},
    # These are listed in https://cloud.google.com/compute/docs/operating-systems/
    # The name strings can be fetched using wrapper.driver.list_images('windows-sql-cloud')
    {
        "name": "sql-std-2012-win-2012-r2",
        "guest_os": "SQL Server 2012 Standard Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-web-2012-win-2012-r2",
        "guest_os": "SQL Server 2012 Web Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-std-2014-win-2012-r2",
        "guest_os": "SQL Server 2014 Standard Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-web-2014-win-2012-r2",
        "guest_os": "SQL Server 2014 Web Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-std-2016-win-2012-r2",
        "guest_os": "SQL Server 2016 Standard Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-std-2016-win-2016",
        "guest_os": "SQL Server 2016 Standard Windows 2016",
        "total_disk_size": 50,
    },
    {
        "name": "sql-web-2016-win-2012-r2",
        "guest_os": "SQL Server 2016 Web Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-web-2016-win-2016",
        "guest_os": "SQL Server 2016 Web Windows 2016",
        "total_disk_size": 50,
    },
    {
        "name": "sql-exp-2017-win-2012-r2",
        "guest_os": "SQL Server 2017 Express Windows 2012 R2",
        "total_disk_size": 50,
    },
    {
        "name": "sql-exp-2017-win-2016",
        "guest_os": "SQL Server 2017 Express Windows 2016",
        "total_disk_size": 50,
    },
    {
        "name": "sql-std-2017-win-2016",
        "guest_os": "SQL Server 2017 Standard Windows 2016",
        "total_disk_size": 50,
    },
    {
        "name": "sql-web-2017-win-2016",
        "guest_os": "SQL Server 2017 Web Windows 2016",
        "total_disk_size": 50,
    },
]


# to update this list of zones, use the libcloud version of get_all_locations
locations = [
    {"id": "2220", "name": "asia-east1-a"},
    {"id": "2221", "name": "asia-east1-b"},
    {"id": "2222", "name": "asia-east1-c"},
    {"id": "2101", "name": "europe-west1-b"},
    {"id": "2104", "name": "europe-west1-d"},
    {"id": "2103", "name": "europe-west1-c"},
    {"id": "2000", "name": "us-central1-a"},
    {"id": "2001", "name": "us-central1-b"},
    {"id": "2002", "name": "us-central1-c"},
    {"id": "2004", "name": "us-central1-f"},
    {"id": "2233", "name": "us-east1-c"},
    {"id": "2234", "name": "us-east1-d"},
    {"id": "2231", "name": "us-east1-b"},
]

"""
Sizes can be found here: https://developers.google.com/compute/pricing
Or here: https://cloud.google.com/compute/docs/machine-types

These can be fetched from the API using the following:
rh = GCEHandler.objects.first()
wrapper, node = rh.get_wrapper_and_node('us-central1-a')
sizes = wrapper.driver.list_sizes()
for size in sizes:
    print '"label": "{}", "cores": "{}", "ram": "{}"'.format(size.name, size.extra['guestCpus'], float(size.ram/256) / 4)

Note: 32-core sizes are not currently returned by list_sizes(), but could be returned as a size
on an existing VM, so they are manually added to the list until they get added to the API.
"""
gce_sizes = [
    {"label": "f1-micro", "cores": "1", "ram": ".6"},
    {"label": "g1-small", "cores": "1", "ram": "1.7"},
    {"label": "n1-standard-1", "cores": "1", "ram": "3.75"},
    {"label": "n1-standard-2", "cores": "2", "ram": "7.5"},
    {"label": "n1-standard-4", "cores": "4", "ram": "15"},
    {"label": "n1-standard-8", "cores": "8", "ram": "30"},
    {"label": "n1-standard-16", "cores": "16", "ram": "60"},
    {"label": "n1-standard-32", "cores": "32", "ram": "120"},
    {"label": "n1-highmem-2", "cores": "2", "ram": "13"},
    {"label": "n1-highmem-4", "cores": "4", "ram": "26"},
    {"label": "n1-highmem-8", "cores": "8", "ram": "52"},
    {"label": "n1-highmem-16", "cores": "16", "ram": "104"},
    {"label": "n1-highmem-32", "cores": "32", "ram": "208"},
    {"label": "n1-highcpu-2", "cores": "2", "ram": "1.8"},
    {"label": "n1-highcpu-4", "cores": "4", "ram": "3.6"},
    {"label": "n1-highcpu-8", "cores": "8", "ram": "7.2"},
    {"label": "n1-highcpu-16", "cores": "16", "ram": "14.4"},
    {"label": "n1-highcpu-32", "cores": "32", "ram": "28.8"},
]
