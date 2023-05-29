#!/usr/bin/perl -w
##################################################################
## Author: Ron Flax
## Email: ron@cloudboltsoftware.com
## 01/28/2013
## v1.2
###################################################################

use strict;
use warnings;

use FindBin;
use lib "/usr/lib/vmware-vcli/apps/";
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../lib/";
use constant false => 0;
use constant true  => 1;

use SCUtil;
use VMware::VIRuntime;
use AppUtil::VMUtil;
use Data::Dumper;

my %opts = (
    'operation' => {
    type => "=s",
    help => "Operation [show|edit|reset]",
    required => 1,
    },
    'dvportgroup' => {
    type => "=s",
    help => "Name of Distributed Portgroup to perform operation on",
    required => 1,
    },
    'dvswitch' => {
    type => "=s",
    help => "Name of Distributed vSwitch to check",
    required => 0,
    },
   'vmuuid' => {
      type => "=s",
      help => "The uuid of the VM",
      required => 1,
   },
   'mac' => {
      type => "=s",
      help => "The mac address of the NIC",
      required => 1,
   }
);
Opts::add_options(%opts);

Opts::parse();
Opts::validate();
Util::connect();

my $operation = Opts::get_option('operation');
my $dvportgroup = Opts::get_option('dvportgroup');
my $dvswitch = Opts::get_option('dvswitch');
my $vmname = "DEPRECATED";
my $vmuuid = Opts::get_option('vmuuid');
my $mac = Opts::get_option('mac');
my $dvSwitches = "";

my $vmware_version = Vim::get_service_content()->about->version;
if (index($vmware_version, "5.") == -1 && index($vmware_version, "6.") == -1) {
    # the version string should start with "5." or "6."
    # Allowing anything after that will protect us from breaking when VMware
    # comes out with 5.6, 6.0, etc.  When they upgrade to 7.x, we'll have to
    # update this, perhaps by adding proper version comparison
    print "\nThis script is only supported on vSphere 5.0 or greater\n";
    print "The version detected is $vmware_version\n\n";
    Util::disconnect();
    exit 1;
}

if($dvswitch) {
    $dvSwitches = Vim::find_entity_views(view_type => 'DistributedVirtualSwitch', filter => {'name' => $dvswitch});
} else {
    $dvSwitches = Vim::find_entity_views(view_type => 'DistributedVirtualSwitch');
}

my $portkey = get_portkey($vmname, $vmuuid, $mac);
my $avail_vlanid = "";
my $vlan_target = "0";

if($operation eq "show" || $operation eq "edit" || $operation eq "reset") {
    foreach my $dvs (sort{$a->name cmp $b->name} @$dvSwitches) {
        print "dvSwitch: " . $dvs->name . "\n";
        # if there are multiple NICs on a VM the actions of this script happen
        # too slowly on vSphere and the script ends up using the same VLAN id
        # multiple times
        sleep(10);
        if(defined($dvs->portgroup)) {
            my $dvPortgroups = $dvs->portgroup;
            foreach my $dvpg (@$dvPortgroups) {
                my $dvpgView = Vim::get_view(mo_ref => $dvpg, properties => ['name','config']);
                if($dvpgView->{'name'} eq $dvportgroup && $dvpgView->{'config'}->type eq 'earlyBinding') {
                    print "dvPortgroup: " . $dvpgView->{'name'};
                    print " has " . $dvpgView->{'config'}->numPorts . " ports\n";

		    # we'll use vlan Id's from 2 - numPorts, so if the portgroup has 128 ports we can assign 
		    # vlan Id's from 2 - 128.  Id's 0 and 1 will not be assigned by us.
		    # here we create an array of vlan Id's and pre-set the values to '0'
		    # as we identify vlan Id's that have been assigned (by walking the list) we will set 
		    # the index of identified vlan Id's to '1'.
		    #
		    # when assigning new ports a vlan Id, the first available '0' entry will be used.
                    my @array_of_vlanids = (0) x $dvpgView->{'config'}->numPorts;
		    $array_of_vlanids[0] = 1; # vlan Id 0 forced to be assigned
		    $array_of_vlanids[1] = 1; # vlan Id 1 forced to be assigned

                    my $vmCriteria = new DistributedVirtualSwitchPortCriteria(connected => 'true',
                                         inside => 'true', portgroupKey => [$dvpgView->{'config'}->key]);
                    my $dvports = $dvs->FetchDVPorts(criteria => $vmCriteria);

		    # walk through the dvports array to determine which vlan Id's have been assigned.
		    foreach my $dvport (@$dvports) {
		        if ($dvport->connectee && $dvport->connectee->connectedEntity->type eq "VirtualMachine") {
			    if (defined($dvport->state->runtimeInfo->vlanIds)) {
			        my $vlans = $dvport->state->runtimeInfo->vlanIds;
				foreach (@$vlans) {
				    if ($_->start eq $_->end) {
				        $array_of_vlanids[$_->start] = 1;
				    }
				}
			    }
			}
		    }

		    # now identify the next available vlan Id we can assign to this port.
                    foreach $avail_vlanid (2 .. ($dvpgView->{'config'}->numPorts - 1)) {
                      if ($array_of_vlanids[$avail_vlanid] eq 0) {
                         $vlan_target = $avail_vlanid;
                         last;
                      }
                    }

                    foreach my $dvport (@$dvports) {
                        if ($dvport->key ne $portkey) {
                            next;
                        }
                        if ($dvport->connectee) {
			    if ($dvport->connectee && $dvport->connectee->connectedEntity->type eq "VirtualMachine") {
                                my $connecteeView = Vim::get_view(mo_ref => $dvport->connectee->connectedEntity, 
                                    properties => ['name']);
                                if ($operation eq "show") {
                                    print "VM: " . $connecteeView->{'name'} . "\n";
                                    print "Device: " . ($dvport->connectee->nicKey ? $dvport->connectee->nicKey : "") . "\n";
                                    print "Link: " . (defined($dvport->state->runtimeInfo->linkUp) ?
                                        ($dvport->state->runtimeInfo->linkUp ? "up" : "down") : "N/A") . "\n";
                                    print "PortId: " . $dvport->key . "\n";
                                    print "Blocked: " . (defined($dvport->state->runtimeInfo->blocked) ?
                                        ($dvport->state->runtimeInfo->blocked ? "true" : "false"): "N/A") . "\n";
                                    print "vlanIds: ";
                                    if (defined($dvport->state->runtimeInfo->vlanIds)) {
                                        my $vlans = $dvport->state->runtimeInfo->vlanIds;
                                        foreach (@$vlans) {
                                            if ($_->start eq $_->end) {
                                                print $_->start . "\n";
                                            } else {
                                                print $_->start . "-" . $_->end . "\n";
                                            }
                                        }
                                    } else {
                                        print "N/A";
                                    }
                                    print "macAddr: " . (defined($dvport->state->runtimeInfo->macAddress) ?
                                        ($dvport->state->runtimeInfo->macAddress): "N/A"). "\n";
                                }
                                elsif($operation eq "edit" || $operation eq "reset") {
                                    # this section should use the ReconfigureDVPort_Task() function to set
                                    # both the vlanid to the assigned vlan and blocked state to unblocked for this port
				    if ($operation eq "edit" && defined($dvport->state->runtimeInfo->vlanIds)) {
				        my $vlans = $dvport->state->runtimeInfo->vlanIds;
					foreach (@$vlans) {
					    if ($_->start eq $_->end && $_->start gt 1) {
					        print "Error: " . $connecteeView->{'name'} . " has aleady been assigned vlan id " . $_->start . "\n";
						Util::disconnect();
						exit;
					    }
					}
				    }
                                    foreach my $dvs (@$dvSwitches) {
                                        if(defined($dvs->portgroup)) {
                                            my $dvPortgroups = $dvs->portgroup;
                                            foreach my $dvpg (@$dvPortgroups) {
                                                my $dvpgView = Vim::get_view(mo_ref => $dvpg, properties => ['name','config.configVersion']);
                                                if($dvpgView->{'name'} eq $dvportgroup) {
                                                    if ($operation eq "edit") {
                                                        print "assigning vlan id $vlan_target to this port.\n";
                                                    }
						    my $boolTrue = new BoolPolicy(inherited => false, value => true);
						    my $boolFalse = new BoolPolicy(inherited => false, value => false);
                                                    my $boolBlocked = ($operation eq "edit" ? $boolFalse : $boolTrue);
                                                    my $config_spec_operation = new ConfigSpecOperation('edit');
                                                    my $vlanspec = new VmwareDistributedVirtualSwitchVlanIdSpec(inherited => 'false',
                                                             vlanId => ($operation eq "edit" ? $vlan_target : 0));
                                                    my $dvportsetting = new VMwareDVSPortSetting(vlan => $vlanspec, blocked => $boolBlocked);

                                                    my $dvpspec = new DVPortConfigSpec(operation => 'edit', key => $portkey,
                                                             setting => $dvportsetting);

						    eval { 
                                                        my $dvPg = Vim::get_view(mo_ref => $dvpg);
                                                        my $dvSw = Vim::get_view(mo_ref => $dvPg->config->distributedVirtualSwitch);
							$dvSw->ReconfigureDVPort(port => $dvpspec);
						    };

                                                    if($@) {
                                                        print "Error: " . $@ . "\n";
                                                    }
                                                    last;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
# TODO: ^- Add more nesting

sub get_portkey {
    my $vmuuid = $_[1];
    my $vmmac  = $_[2];
    my $vm = SCUtils::get_vm($vmuuid);

    my $devices = $vm->config->hardware->device;
    foreach my $device (@$devices) {
        my $devInfoLabel = substr($device->deviceInfo->label, 0, length($device->deviceInfo->label) -1);
        if ($devInfoLabel eq 'Network adapter ') {
            if ($device->macAddress eq $vmmac) {
                return ($device->backing->port->portKey);
            }
        }
    }
}

Util::disconnect();
