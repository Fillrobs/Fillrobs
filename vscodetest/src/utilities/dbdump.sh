#!/bin/bash

set -e

#------------------------------------------------------------------------------
db="cloudbolt";
dt=`date +%F-%H%M`;
fname="$db-$dt.sql";
dest="~/sql-dumps/";

#------------------------------------------------------------------------------
# $1=$dbuser
if [ -n "$1" ]; then
  dbuser=$1
else
  echo "Parameter 1 must be the database username."
  exit 1
fi

# $2=$dbpass
if [ -n "$2" ]; then
  dbpass=$2
else
  echo "Parameter 2 must be the database password for $dbuser."
  exit 1
fi

#------------------------------------------------------------------------------
if [ ! -d $dest ]; then
  mkdir $dest
fi

echo "Dumping $db to $dest$fname";
mysqldump -u $dbuser --password=$dbpass $db > ~/sql-dumps/$fname
