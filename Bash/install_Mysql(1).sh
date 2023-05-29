#!/bin/bash -e

python -mplatform | grep -qi ubuntu
is_ubuntu=$?


# Original script taken from http://stackoverflow.com/questions/34569373/install-mysql-community-server-5-7-via-bash-shell-script-in-centos-7-x64

mysqlRootPass='{{ server.database_password }}'

echo ' -> Removing previous mysql server installation'
if [ $is_ubuntu -eq 0 ]; then
apt-get remove --purge mysql-server mysql-client mysql-common -y
apt-get autoremove -y
apt-get autoclean
rm -rf /etc/mysql
else
service mysqld stop && yum remove -y mysql-server && rm -rf /var/lib/mysql && rm -rf /var/log/mysqld.log && rm -rf /etc/my.cnf
fi
echo ' -> Installing mysql server (community edition)'
#yum localinstall -y https://dev.mysql.com/get/mysql57-community-release-el7-7.noarch.rpm

if [ $is_ubuntu -eq 0 ]; then
apt-get install mysql-server
else
yum install -y mysql-server
echo ' -> Starting mysql server (first run)'
/sbin/chkconfig --levels 235 mysqld on 
service mysqld start
fi
tempRootDBPass="`grep 'temporary.*root@localhost' /var/log/mysqld.log | tail -n 1 | sed 's/.*root@localhost: //'`"

echo " -> Setting up new mysql server root password (tmp pass = $tempRootDBPass)"
if [ $is_ubuntu -eq 0 ]; then
service mysql stop
service mysql start
else
service mysqld stop
rm -rf /var/lib/mysql/*logfile*
service mysqld start
fi
mysqladmin -u root --password="$tempRootDBPass" password "$mysqlRootPass"
mysql -u root --password="$mysqlRootPass" <<-EOSQL
    DELETE FROM mysql.user WHERE User='';
    DROP DATABASE IF EXISTS test; 
    DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'; 
    DELETE FROM mysql.user where user != 'mysql.sys'; 
    CREATE USER 'root'@'%' IDENTIFIED BY '${mysqlRootPass}';
    GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
EOSQL
echo " -> MySQL server installation completed."