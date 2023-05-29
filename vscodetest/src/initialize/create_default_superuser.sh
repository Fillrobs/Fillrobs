#!/bin/bash

my_script=$0
my_dir=`dirname $my_script`
test "$my_dir" == "." && my_dir=`pwd`
cd $my_dir/..

. initialize/cb_default_superuser
test -f install_config && . install_config

initialize/create_superuser.py -u "$superuser_name" -p "$superuser_password" -f "$superuser_first" -l "$superuser_last" -e "$superuser_email"
