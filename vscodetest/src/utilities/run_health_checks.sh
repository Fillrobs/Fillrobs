#!/bin/sh

source /opt/cloudbolt/install_config

if [ -z "${python_exec}" ] ; then
    python_exec="python"
fi

mydir=`dirname $0`
my_src_dir=`(cd $mydir/..; pwd)`

export PYTHONPATH=$my_src_dir
cmd="${python_exec} $my_src_dir/jobengine/jobmodules/healthcheckjob.py"

$cmd
