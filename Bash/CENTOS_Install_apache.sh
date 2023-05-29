#!/bin/bash
echo "Database Password : {{server.WordPress_Database_Password}}"
#Install Apache, FirewallD and Word Press Pre-Reqs
yum install -y httpd php php-common php-mysql php-gd php-xml php-mbstring php-mcrypt firewalld

systemctl enable httpd

setsebool -P httpd_can_network_connect 1

#start firewall
systemctl enable firewalld
systemctl start firewalld

# Open up incoming traffic on TCP ports 80 & 443
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent

firewall-cmd --reload