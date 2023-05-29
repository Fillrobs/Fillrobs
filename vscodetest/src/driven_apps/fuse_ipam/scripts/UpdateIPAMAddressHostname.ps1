$ipAddress = "{{ip_address}}"
$new_hostname = "{{new_hostname}}"
$ipamServer = "{{ipamServer}}"
$cim = new-cimsession -ComputerName $ipamServer
$ErrorActionPreference = "stop"

if( $ipAddress -ne $null){
    Set-IpamAddress -CimSession $cim -IpAddress $ipAddress -devicename $new_hostname
    write-host "success";
    exit 0
} else {
    write-host "Failed to update " $ipAddress " with new hostname " $new_hostname;
    exit 1
}
