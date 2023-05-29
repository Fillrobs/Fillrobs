#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

ROOT_SQL_PASS='{{ mysql_database_password }}'
debconf-set-selections <<< "mysql-server mysql-server/root_password password $ROOT_SQL_PASS"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $ROOT_SQL_PASS"
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server

chmod 777 /etc/mysql/my.cnf
echo -e "[client]\nuser = root\npassword = M3tsiT3ch123" >> /etc/mysql/my.cnf
chmod 400 /etc/mysql/my.cnf

echo -------------------------------------#
echo 'Configuring mysql database securely.'
echo -------------------------------------#

sleep 2

#MySQL secure installation
#mysql -e "SET PASSWORD for 'root'@'localhost' = PASSWORD('M3tsiT3ch123');"
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'M3tsiT3ch123';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -e "FLUSH PRIVILEGES;"

echo ---------------------------------#
echo 'Opening port 3306, just in case.'
echo ---------------------------------#

sleep 2

#check to make sure port 3306 is open - port will be opened for input and output after this command
iptables -A INPUT -p tcp -s 10.22.14.0/24 --dport 3306 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp --sport 3306 -m conntrack --ctstate ESTABLISHED -j ACCEPT

echo -------------------------------------------------------#
echo 'Creating table, user and privileges in mysql database.'
echo -------------------------------------------------------#


sleep 3

#open mysql, create new user, create table (mysql non-interactive)
mysql -e "use mysql;"
mysql -e "create user 'metsiuser'@'localhost' identified by 'M3tsiT3ch123';"
mysql -e "show databases;"

echo --------------------------------#
echo 'Shown to have no test database.'
echo --------------------------------#




# Tell the user the script is finished
echo ----------------------------------#
echo "Install Script has finished"
echo ----------------------------------#

# Logging to /var/log/installs_log.txt

DATE=$(date)
#USER = 'CloudBolt'

echo -e "mysql secure install was started -done by CloudBolt at " time "\n $DATE \n" >> /var/log/installs_log.txt
echo -e "if mysql installed, it was purged -done by CloudBolt at " time"\n $DATE \n" >> /var/log/installs_log.txt
echo -e "mysql has been installed -done by CloudBolt at " time "\n $DATE \n" >> /var/log/installs_log.txt
echo -e "port 3306 opened -done by CloudBolt at " time "\n $DATE \n" >> /var/log/installs_log.txt
echo -e "new user metsiuser + table it-410 made -done by CloudBolt at " time "\n \n $DATE" >> /var/log/installs_log.txt
echo -e "mysql secure install completed by CloudBolt at " time\n " $DATE \n" >> /var/log/installs_log.txt
