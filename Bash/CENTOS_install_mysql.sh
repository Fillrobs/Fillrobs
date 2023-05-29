#!/bin/bash -e

# Original script taken from http://stackoverflow.com/questions/34569373/install-mysql-community-server-5-7-via-bash-shell-script-in-centos-7-x64

mysqlRootPass="{{server.WordPress_Database_Password}}"

echo ' -> Installing mysql server (community edition)'

yum localinstall -y https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm

yum install -y mysql-community-server firewalld

systemctl enable firewalld
systemctl start firewalld

echo ' -> Starting mysql server (first run)'
/sbin/chkconfig --levels 235 mysqld on 
service mysqld start

tempRootDBPass="`grep 'temporary.*root@localhost' /var/log/mysqld.log | tail -n 1 | sed 's/.*root@localhost: //'`"

echo " -> Setting up new mysql server root password"
echo "New mysql root pass : {{server.WordPress_Database_Password}}"
service mysqld stop
rm -rf /var/lib/mysql/*logfile*
service mysqld start
mysqladmin -u root --password="$tempRootDBPass" password "$mysqlRootPass"
mysql -u root --password="$mysqlRootPass" <<-EOSQL
    UNINSTALL PLUGIN validate_password;
    DELETE FROM mysql.user WHERE User='';
    DROP DATABASE IF EXISTS test; 
    DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'; 
    DELETE FROM mysql.user where user != 'mysql.sys'; 
    CREATE USER 'root'@'%' IDENTIFIED BY '${mysqlRootPass}';
    GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
EOSQL
echo " -> MySQL server installation completed."

echo "============================================"
echo "WordPress Database Setup"
echo "============================================"
dbname='wordpress'
dbuser='wordpress_user'

echo {{blueprint_context.apptier.server.ip}}
echo "CREATE USER '${dbuser}'@'{{blueprint_context.apptier.server.ip}}';"
echo "SET PASSWORD FOR '${dbuser}'@'{{blueprint_context.apptier.server.ip}}'= PASSWORD('"${mysqlRootPass}"');"
echo "GRANT ALL PRIVILEGES ON $dbname.* TO '${dbuser}'@'{{blueprint_context.apptier.server.ip}}' IDENTIFIED BY '${mysqlRootPass}';"
echo "Creating database with the name '$dbname'..."
mysql -u root --password="$mysqlRootPass" <<-EOSQL
  CREATE DATABASE $dbname;
  CREATE USER '${dbuser}'@'{{blueprint_context.apptier.server.ip}}';
  SET PASSWORD FOR '${dbuser}'@'{{blueprint_context.apptier.server.ip}}'= PASSWORD('"${mysqlRootPass}"');
  GRANT ALL PRIVILEGES ON $dbname.* TO '${dbuser}'@'{{blueprint_context.apptier.server.ip}}' IDENTIFIED BY '${mysqlRootPass}';
  FLUSH PRIVILEGES;
EOSQL

echo "WordPress Database Setup completed"


# Open up incoming traffic on TCP ports 3306
firewall-cmd --zone=public --add-port=3306/tcp --permanent

firewall-cmd --reload