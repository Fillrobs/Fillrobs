#!/bin/bash
echo "Variables start"
echo "Database Server IP : {{blueprint_context.dbtier.server.ip}}"
echo "Database Password : {{server.WordPress_Database_Password}}"
echo "WordPress Title : {{server.WordPress_Title}}"
echo "WordPress Admin User : {{server.Admin_User}}"
echo "WordPress Admin Password : {{server.Admin_Password}}"
echo "Variables end"
#Install Wordpress and Pre-reqs
yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -y
yum install http://rpms.remirepo.net/enterprise/remi-release-7.rpm -y

yum install yum-utils -y
yum-config-manager --enable remi-php56   [Install PHP 7.6] -y
yum install php php-common php-mysql php-gd php-xml php-mbstring php-mcrypt php-cli php-curl php-ldap php-zip php-fileinfo perl wp-cli -y

# download wordpress into /tmp
cd /tmp
curl -O https://wordpress.org/latest.tar.gz
# unzip wordpress
tar -zxf latest.tar.gz
# change dir to wordpress
cd wordpress

#create wp config
dbhost="{{blueprint_context.dbtier.server.ip}}"
dbname='wordpress'
dbuser='wordpress_user'
dbpass='{{server.WordPress_Database_Password}}'


cp wp-config-sample.php wp-config.php
#set database details with perl find and replace
sed -i "s/localhost/$dbhost/g" wp-config.php
sed -i "s/database_name_here/$dbname/g" wp-config.php
sed -i "s/username_here/$dbuser/g" wp-config.php
sed -i "s/password_here/$dbpass/g" wp-config.php

#set WP salts
perl -i -pe'
  BEGIN {
    @chars = ("a" .. "z", "A" .. "Z", 0 .. 9);
    push @chars, split //, "!@#$%^&*()-_ []{}<>~\`+=,.;:/?|";
    sub salt { join "", map $chars[ rand @chars ], 1 .. 64 }
  }
  s/put your unique phrase here/salt()/ge
' wp-config.php

#create uploads folder and set permissions
mkdir -p wp-content/uploads
chmod 775 wp-content/uploads

echo "Copying WordPress files to /var/www/html..."

cp -r /tmp/wordpress/* /var/www/html
service httpd restart

echo "Cleaning wordpress download..."
rm ../latest.tar.gz

echo "==================================="
echo "WordPress Installation is complete."
echo "==================================="

wp core install --url={{blueprint_context.apptier.server.ip}} --title="{{server.WordPress_Title}}" --admin_user={{server.Admin_User}} --admin_password={{server.Admin_Password}} --admin_email=info@example.com --allow-root

echo "==================================="
echo "WordPress Installation is complete."
echo "==================================="