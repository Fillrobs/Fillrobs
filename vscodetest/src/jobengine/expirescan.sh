mydir=`dirname $0`
my_src_dir=`(cd $mydir/..; pwd)` 
lockfile=$my_src_dir/expirescan.lock

# already running?  If so, just exit
if [ -f $lockfile ]; then
    ps -ef | grep ^$USER | grep -v grep |grep -q expirescan.py
    if [ $? -eq 1 ]; then
        echo "A lockfile ($lockfile) exists, but the expire scan does not seem to be running."
        echo "Exiting anyway, this needs to be looked at by a CloudBolt admin."
    else
        echo "expirescan.py is already running, exiting."
    fi
    exit 1
fi

if [ -f $my_src_dir/install_config ] ; then
    source $my_src_dir/install_config
fi

if [ -z "${python_exec}" ] ; then
    python_exec="/usr/local/bin/python"
fi

touch $lockfile
export PYTHONPATH=$my_src_dir 
test -f $mydir/expirescan.pyc && expirescan=$mydir/expirescan.pyc
test -f $mydir/expirescan.py && expirescan=$mydir/expirescan.py
cmd="${python_exec} $expirescan"

# run it!
$cmd
rv=$?
rm $lockfile
exit $rv
