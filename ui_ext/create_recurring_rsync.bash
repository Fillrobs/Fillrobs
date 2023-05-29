#!/bin/sh

sshpass -f rsync_pass  rsync -ah -P --exclude '.venv' /mnt/g/Metsi2/CloudBolt/Scripts/ui_ext/create_recurring_job/ root@10.114.4.9:/var/opt/cloudbolt/proserv/xui/create_recurring_job/
sshpass -f rsync_pass ssh root@10.114.4.9 chown apache: -R /var/opt/cloudbolt/proserv/xui/create_recurring_job/
