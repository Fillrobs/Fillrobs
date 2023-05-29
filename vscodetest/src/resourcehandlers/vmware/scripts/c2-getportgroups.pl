#!/usr/bin/perl 
#
# Copyright (c) 2007 VMware, Inc.  All rights reserved.
#

use strict;
use warnings;

use Switch;
use FindBin;
#use lib "$FindBin::Bin/../";
use lib "/usr/lib/vmware-vcli/apps/";
use lib "$FindBin::Bin/../lib/";
use SCUtil;
use constant false => 0;
use constant true  => 1;

use VMware::VIRuntime;
use XML::LibXML;
use AppUtil::XMLInputUtil;
use AppUtil::HostUtil;

$Util::script_version = "1.0";

my %opts = (
    clustername => {
        type => "=s",
        help => "The cluster to check against",
        required => 0
    },
    switchname => {
      type => "=s",
      help => "The dvSwitch that should contain the portgroup",
      required => 1
    },
    prefix => {
      type => "=s",
      help => "The portgroup prefix to match against",
      required => 1
    }
);

Opts::add_options(%opts);
Opts::parse();

Util::connect();
find_portgroups();
Util::disconnect();


# ========================
sub find_portgroups {

    my $override = Sub::Override->new( 'EntityViewBase::get_search_filter_spec' => \&SCUtils::get_search_filter_spec2);
    my $clustername = Opts::get_option('clustername');
    my $switchname = Opts::get_option('switchname');
    my $pgprefix = Opts::get_option('prefix');

    my $cluster_view = Vim::find_entity_view(view_type => 'ClusterComputeResource',
                                filter => {'name' => $clustername });

    my $dc = SCUtils::get_datacenter( $cluster_view->parent);
    my $result = SCUtils::get_entities(view_type => 'Network', obj => $dc);
    foreach (@$result) {
       my $obj_content = $_;
       my $mob = $obj_content->obj;
       my $dvpg = Vim::get_view(mo_ref=>$mob);
       if(ref($dvpg) . "" eq "DistributedVirtualPortgroup") {
           if ((!$pgprefix) or (index($dvpg->name, $pgprefix) == 0)) {
               my $dvs_mor = $dvpg->config->distributedVirtualSwitch;
               my $dvs_obj = Vim::get_view(mo_ref=>$dvs_mor);
               if ($dvs_obj->name . "" eq $switchname) {
                   print $dvpg->name  . "SCDIV";
                   if ($dvpg->vm) {
                       #print $dvpg->name . " is in use.\n";
                       my @arr = Vim::get_views(mo_ref_array => $dvpg->vm);
                       my @vms = shift(@arr);
                       my $vm = shift(@vms);
                       print shift(@$vm)->config->uuid . "\n";

                   } else {
                        #print "Found free portgroup: " . $dvpg->name . "\n";
                        print "-----\n";
                   } 
               }
           }
        }
    }
}
