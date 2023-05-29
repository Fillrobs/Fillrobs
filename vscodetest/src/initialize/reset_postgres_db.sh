#!/bin/bash

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

if [ -z "$dbhost" ]; then
    dbhost="localhost"
fi
if [ -z "$dbport" ]; then
    dbport="5432"
fi

# have django create our baseline CloudBolt database schema
echo $ruler
echo "$pre Creating django baseline schema"
${python_exec} manage.py migrate --noinput
database_migration_return=$?
echo "* database_migration_return: $database_migration_return"
test $database_migration_return -gt 0 && exit $database_migration_return

# create the GlobalPreferences object
echo $ruler
echo "$pre Creating GlobalPreferences"
initialize/create_global_preferences.py
global_preferences_return=$?
echo "* global_preferences_return: $global_preferences_return"
echo "* default_superuser_return: $default_superuser_return"
echo "* default_minimal_return: $default_minimal_return"

test $global_preferences_return -gt 0 && exit $global_preferences_return

# create a default superuser
echo $ruler
echo "$pre Creating a Super User"
initialize/create_default_superuser.sh
default_superuser_return=$?
test $default_superuser_return -gt 0 && exit $default_superuser_return

# create basic data, if required
if [ "$force" != "nodata" ]; then
    echo $ruler
    echo "$pre Creating basic custom fields [mem_size, cpu_cnt, disk_size, etc]"
    initialize/create_objects.py initialize/cb_minimal.py
    default_minimal_return=$?
else
    default_minimal_return="N/A"
fi
test $default_minimal_return -gt 0 && exit $default_minimal_return

echo $ruler
echo "
Now either login with the super user account created above and configure CloudBolt
from its UI, or edit initialize/cb_objects.py to meet your needs, and run
initialize/create_objects.py to have everything created accordingly.
"

exit 0
