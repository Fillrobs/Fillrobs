#!/bin/sh

my_script=$0
my_dir=`dirname $my_script`
test "$my_dir" == "." && my_dir=`pwd`
cd $my_dir

# Bernard Sanders 2/24/12
# Script to create some base data that can be used to show CloudBolt 
# functionality.  Useful when you don't have access to 100s/1000s of VMs
# but still want to see what the product would look like if you did.
# Should be run after create_objects.py creates the basic data

# this script will create:
#  - fake servers
#  - fake server history (TODO)
#  - fake license data

./create_fake_servers.py --hostname-prefix 'mgdvm-A-' --ip-prefix '192.168.30.' -g 'Stocks' -e 'Sydney Dev Lab' -u bernard -n 24 -c mem_size=4:cpu_cnt=4:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-B-' --ip-prefix '192.168.31.' -g 'Bonds' -e 'Seoul Xen Env' -u auggy -n 19 -c mem_size=4:cpu_cnt=4:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-C-' --ip-prefix '192.168.32.' -g 'NY Trading Servers' -e 'NYC Xen Env' -u bernard -n 8 -c mem_size=8:cpu_cnt=4:disk_size=30
./create_fake_servers.py --hostname-prefix 'mgdvm-D-' --ip-prefix '192.168.33.' -g 'Boston Trading Servers' -e 'NYC Xen Env' -u bernard -n 3 -c mem_size=8:cpu_cnt=2:disk_size=30
./create_fake_servers.py --hostname-prefix 'mgdvm-D-' --ip-prefix '192.168.33.' -g 'International' -e 'Seoul Xen Env' -u bernard -n 5 -c mem_size=4:cpu_cnt=1:disk_size=10

./create_fake_servers.py --hostname-prefix 'mgdvm-M-' --ip-prefix '192.168.50.' -g 'Wealth Management' -e 'Atlanta Xen Env' -u thamlin -n 21 -c mem_size=4:cpu_cnt=4:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-N-' --ip-prefix '192.168.51.' -g 'Americas' -e 'NYC Xen Env' -u thamlin -n 10 -c mem_size=4:cpu_cnt=2:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-O-' --ip-prefix '192.168.52.' -g 'Americas' -e 'Denver Xen Lab' -u thamlin -n 8 -c mem_size=4:cpu_cnt=2:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-P-' --ip-prefix '192.168.53.' -g 'Americas' -e 'San Jose QA Lab' -u thamlin -n 3 -c mem_size=4:cpu_cnt=2:disk_size=50
./create_fake_servers.py --hostname-prefix 'mgdvm-Q-' --ip-prefix '192.168.54.' -g 'APAC' -e 'Hong Kong QA Lab' -u auggy -n 20 -c mem_size=4:cpu_cnt=4:disk_size=50

./create_fake_quotas.py
./create_fake_license_data.py
