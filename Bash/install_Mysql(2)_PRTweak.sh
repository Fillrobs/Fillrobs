#!/bin/bash -e

# Original script taken from http://stackoverflow.com/questions/34569373/install-mysql-community-server-5-7-via-bash-shell-script-in-centos-7-x64

mysqlRootPass='{{ server.database_password }}'

echo ' -> Removing previous mysql server installation'
service mysqld stop && yum remove -y mysql-server && rm -rf /var/lib/mysql && rm -rf /var/log/mysqld.log && rm -rf /etc/my.cnf

echo ' -> Installing mysql server (community edition)'
#yum localinstall -y https://dev.mysql.com/get/mysql57-community-release-el7-7.noarch.rpm

# taken from https://www.linode.com/docs/guides/how-to-install-mysql-on-centos-7/
yum -y update
yum install -y wget

cd /home/

wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum update -y

yum install -y mysql-server

echo ' -> Starting mysql server (first run)'
/sbin/chkconfig --levels 235 mysqld on 
service mysqld start

# initial password is blank
#tempRootDBPass="`grep 'temporary.*root@localhost' /var/log/mysqld.log | tail -n 1 | sed 's/.*root@localhost: //'`"

echo " -> Setting up new mysql server root password (initial pass is blank)"
service mysqld stop
rm -rf /var/lib/mysql/*logfile*
service mysqld start
mysqladmin -u root password "$mysqlRootPass"
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