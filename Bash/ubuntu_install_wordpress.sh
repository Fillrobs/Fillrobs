#!/bin/bash
clear
echo "============================================"
echo "WordPress Install Script"
echo "============================================"
dbname = '{{ wordpress_dbname }}'
echo "Database Name: $dbname"
dbuser = '{{ wordpress_dbuser }}'
echo "Database User: $dbuser"
dbpass = '{{ wordpress_dbpass }}'
echo "Database Password: $dbpass"
echo "============================================"
echo "A robot is now installing WordPress for you."
echo "============================================"
#download wordpress
cd /tmp

curl -O https://wordpress.org/latest.tar.gz
#unzip wordpress
tar -zxvf latest.tar.gz
#change dir to wordpress
cd wordpress
#create wp config
cp wp-config-sample.php wp-config.php
#set database details with perl find and replace
perl -pi -e "s/DB_NAME/$dbname/g" wp-config.php
perl -pi -e "s/DB_USER/$dbuser/g" wp-config.php
perl -pi -e "s/DB_PASSWORD/$dbpass/g" wp-config.php

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
mkdir wp-content/uploads
chmod 775 wp-content/uploads
echo "Cleaning..."
#remove zip file
rm latest.tar.gz

echo "Copying WordPress files to /var/www/html..."

cp -r /tmp/wordpress/* /var/www/html

echo "========================="
echo "Installation is complete."
echo "========================="
