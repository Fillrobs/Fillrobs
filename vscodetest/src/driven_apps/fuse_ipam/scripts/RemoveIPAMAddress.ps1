Function ValidateValidSubnet{
    Param ([string]$a)
    write-host $a
    $IPregex=‘(?<Address>((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))’
    If ($a -Match $IPregex){return "true"}
}

$ipaddress = "{{ipaddress}}"
$ipamServer = "{{ipamServer}}"

$cim = new-cimsession -ComputerName $ipamServer

$result = ValidateValidSubnet $ipaddress
write-host "result: " $result
if($result -eq "true"){
write-host $ipaddress
Remove-IpamAddress -CimSession $cim -IpAddress $ipaddress -Force
}
Remove-CimSession -CimSession $cim
