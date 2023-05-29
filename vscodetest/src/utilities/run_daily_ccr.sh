mydir=`dirname $0`
my_src_dir=`(cd $mydir/..; pwd)` 
lockfile=$my_src_dir/daily_ccr.lock

# define the output dir for ccrs
ccr_dir="/tmp"

# already running?  If so, just exit
if [ -f $lockfile ]; then
    ps -ef | grep ^$USER | grep -v grep |grep -q run_daily_ccr.py
    if [ $? -eq 1 ]; then
        echo "A lockfile ($lockfile) exists, but run_daily_ccr does not seem to be running."
        echo "Exiting anyway, this needs to be looked at by a CloudBolt admin."
    else
        echo "run_daily_ccr.py is already running, exiting."
    fi
    exit 1
fi

if [ -f $my_src_dir/install_config ] ; then
    source $my_src_dir/install_config
fi

if [ -z "${python_exec}" ] ; then
    python_exec="python"
fi

touch $lockfile
export PYTHONPATH=$my_src_dir 
test -f $mydir/run_daily_ccr.pyc && daily_ccr=$mydir/run_daily_ccr.pyc
test -f $mydir/run_daily_ccr.py && daily_ccr=$mydir/run_daily_ccr.py
cmd="${python_exec} $daily_ccr $ccr_dir"

# run it!
$cmd
rv=$?
rm $lockfile
exit $rv
