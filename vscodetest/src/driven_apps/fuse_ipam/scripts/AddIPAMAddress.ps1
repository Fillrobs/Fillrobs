$subnets = @({{subnets}})
$gateways = @({{gateways}})
$networks = @({{networks}})
$excludedIps = @({{excludedIps}})
$netmasks = @({{netmasks}})
$hostname = "{{hostname}}"
$ipamServer = "{{ipamServer}}"
$cim = new-cimsession -ComputerName $ipamServer
$boundCounter = -1
$numExcluded = $excludedIps.Length+1
#warningPreference of 'silentlycontinue' allows script to continue and keeps 'not enough ips' from bubbling up
$WarningPreference = "silentlycontinue"
$ErrorActionPreference = "stop"

#write-host "acting as: user : $env:UserName / domain : $env:UserDomain / computername : $env:ComputerName"

Function ValidateValidSubnet{
    Param ([string]$a)
    $IPregex=‘(?<Address>((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))’
    If ($a -Match $IPregex){
    return "true"
    }
}

Function AddressIsAvailable([string]$addressIn, [string[]] $excludesIn) {
    foreach ($excludedAddr in $excludesIn) {
       if($addressIn -eq $excludedAddr){
            write "address match"$addressIn
            return "false"
       }
    }

    return "true"
}

Function FetchAddress($subnetIn,$numExcludedIn,$cimIn) {
    $newIp=""
    $ipobj = $subnetIn |get-ipamrange|find-ipamfreeaddress -NumAddress $numExcludedIn -CimSession $cimIn
    if($ipobj -eq $null -or $ipobj -eq $warning_caught){
      return $null
    }

    foreach ($ipadd in $ipobj){
        $isAvailable = AddressIsAvailable $ipadd.IpAddress $excludedIps
        if( $isAvailable -eq "true" ) {
            $newIp = $ipadd.IpAddress
        }
    }
    return $newIp
}

foreach($subnet in $subnets){
    $boundCounter = $boundCounter+1
    Write-host "Trying to get IP from MS IPAM for Subnet $subnet"
    try {
        $result = ValidateValidSubnet $subnet
        if($result -eq "true"){
           $subnet = Get-IpamSubnet -AddressFamily IPv4 -NetworkType NonVirtualized -CimSession $cim | where {$_.NetworkId -eq $subnet}
#           write "setting ipAddress.."
           $ipAddress = FetchAddress $subnet $numExcluded $cim
        }
    } Catch {
        Write-host "no usable addresses in $subnet"
    }

    if( ($ipAddress.Address -ne $null) -and ($ipAddress.Address -ne "") ){
        break
    }
}

if( $ipAddress.Address -ne $null){
    write-host "IP:" $ipAddress.IPAddressToString "," $subnets[$boundCounter] "," $gateways[$boundCounter] "," $networks[$boundCounter] "," $netmasks[$boundCounter];
	Add-IpamAddress -CimSession $cim -IpAddress $ipAddress.IPAddressToString -devicename $hostname
    exit 0
} else {
    exit 1
}
