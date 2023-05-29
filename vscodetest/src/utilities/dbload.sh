#!/bin/bash

set -e

#------------------------------------------------------------------------------
db="cloudbolt";

#------------------------------------------------------------------------------
# $1=$fname
if [ -n "$1" ]; then
  if [ -e "$1" ]; then
    fname=$1
  else
    echo "Parameter 1 must be the filename to load the database from, but $1 was not a file."
    exit 1
  fi
else
  echo "Parameter 1 must be the filename to load the database from."
  exit 1
fi

# $2=$dbuser
if [ -n "$2" ]; then
  dbuser=$2
else
  echo "Parameter 2 must be the database username."
  exit 1
fi

# $3=$dbpass
if [ -n "$3" ]; then
  dbpass=$3
else
  echo "Parameter 3 must be the database password for $dbuser."
  exit 1
fi

#------------------------------------------------------------------------------
echo "Making a backup of $db..."
dbdump $2 $3

echo "Dropping $db...";
python /opt/cloudbolt/manage.py reset_db;

echo "Loading $fname into $db...";
mysql -u $dbuser --password=$dbpass $db < $fname

