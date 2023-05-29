#!/bin/sh

sshpass -f rsync_pass  rsync -ah -P --exclude '.venv' /mnt/g/Metsi2/Cloudbolt/Scripts/ui_ext/azure/azure_server_health_status/ root@10.22.14.21:/var/opt/cloudbolt/proserv/xui/azure_server_health_status/
sshpass -f rsync_pass ssh root@10.22.14.21 chown apache: -R /var/opt/cloudbolt/proserv/xui/azure_server_health_status/

#sshpass -f rsync_pass  rsync -ah -P --exclude '.venv' /mnt/g/Metsi2/Cloudbolt/Scripts/ui_ext/azure/azure_server_health_status/ root@10.22.14.22:/var/opt/cloudbolt/proserv/xui/azure_server_health_status/
#sshpass -f rsync_pass ssh root@10.22.14.22 chown apache: -R /var/opt/cloudbolt/proserv/xui/azure_server_health_status/

sshpass -f rsync_pass ssh root@10.22.14.21 service httpd restart
sshpass -f rsync_pass ssh root@10.22.14.22 service httpd restart
