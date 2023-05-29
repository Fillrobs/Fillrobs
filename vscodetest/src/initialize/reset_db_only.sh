#!/bin/bash

# This script deletes a CB DB completely and recreates it fresh, without
# loadinig any minimal data (like reset_db.sh does).  This is useful if a DB
# gets into a bad state and you want to clean it to the point where you would
# do a DB import of another dataset

if [ -r /opt/cloudbolt/install_config ] ; then
    echo "INFO: Executing /opt/cloudbolt/install_config..."
    source /opt/cloudbolt/install_config
else
    echo "INFO: /opt/cloudbolt/install_config was not executed because it does not exist or is not readable."
fi

if [ -z "${python_exec}" ] ; then
    python_exec="python"
fi

force="$1"
my_script=$0
my_dir=`dirname $my_script`
test "$my_dir" == "." && my_dir=`pwd`

cd $my_dir/..

export DJANGO_SETTINGS_MODULE=settings

ruler="===================================================================="
pre="************ RESET CLOUDBOLT DATABASE: "

if [ "$force" != "force" ] && [ "$force" != "nodata" ]; then
    echo $ruler
    echo " **** WARNING! WARNING! WARNING!"
    echo " **** This script will remove ALL CloudBolt Data!"
    echo " **** If you are absolutely sure this is what you want, please press Y now!"
    echo " **** (run this script with 'force' as an arg to skip this prompt)"

    read kill_switch
    [ "$kill_switch" != "Y" ] && echo "Y not pressed, will not reset CloudBolt Database!" &&  exit 1
fi

# parse settings.py or settings_local.py for the database connection info
settings_file="settings.py"
importline="from settings import *"
dbuser=`${python_exec} -c "$importline;print(DATABASES['default']['USER'])"`
dbpass=`${python_exec} -c "$importline;print(DATABASES['default']['PASSWORD'])"`
dbname=`${python_exec} -c "$importline;print(DATABASES['default']['NAME'])"`
dbhost=`${python_exec} -c "$importline;print(DATABASES['default']['HOST'])"`
dbport=`${python_exec} -c "$importline;print(DATABASES['default']['PORT'])"`

### drop all tables in the database named $dbname
echo $ruler
echo "$pre dropping and recreating database $dbname"
## OLD mysqldump method
## this fails with FK constraints
##mysqldump -u "$dbuser" -p"$dbpass" --add-drop-table --no-data "$dbname" | grep ^DROP | mysql -u "$dbuser" -p"$dbpass" "$dbname"

## OLD manage.py method
## this fails to create the db if it does not already exist, switching to mysql queries
#${python_exec} manage.py reset_db --router=default --noinput

## NEW mysql DROP/CREATE method
# errors in drop are ignorable
echo "DROP DATABASE $dbname" | mysql -u "$dbuser" -p"$dbpass" -h"$dbhost" -P"$dbport" 2>&1
echo "CREATE DATABASE $dbname CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" | mysql -u "$dbuser" -p"$dbpass" -h"$dbhost" -P"$dbport" 2>&1
database_delete_return=$?

exit $database_delete_return
