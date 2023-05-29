 Import-Module DnsServer

$hostname = "{{hostname}}"
$ip = "{{ip}}"
$name = "{{name}}"
$value = "{{value}}"
$dnsServer = "{{dns_server}}"
$releaseARecord = {{release_a_record}}#$true
$releasePtrRecord = {{release_ptr_record}}#$true
$releaseCNameRecord = {{release_cname_record}}
$reverseZone = ""
$domain = ""
$shortName = ""
$errorStr = ""

$vals = $hostname.split(".")
if ( $vals.Length -lt 2 ) {
  Write-Error "Hostname format incorrect $hostname"
} elseif ( $vals.Length -eq 2 ) {
  $domain = $hostname
  $shortName = "."
} else {
  $shortName = $vals[0];
  $domain=$vals[1..($vals.Length-1)] -join "."
}

Write-Host("Domain: $domain")
Write-Host("ShortName: $shortName")

# Get Reverse DNS Zone

function Write-StdErr {
	param ([PSObject] $InputObject)
	$outFunc = if ($Host.Name -eq 'ConsoleHost') {
		[Console]::Error.WriteLine
	} else {
		$host.ui.WriteErrorLine
	}
	if ($InputObject) {
		[void] $outFunc.Invoke($InputObject.ToString())
	} else {
		[string[]] $lines = @()
		$Input | % { $lines += $_.ToString() }
		[void] $outFunc.Invoke($lines -join "`r`n")
	}
}


if ( $releasePtrRecord -eq $true ) {
	$octets = $ip.split(".")
	if ( $octets.Length -ne 4 ) {
	Write-StdErr "IP address is invalid. $ip"
	exit 1
	}
	$revoctets = $ip.split(".")
	[array]::Reverse($revoctets)

	$x=0;
	While ( $x -lt 3 ) {
		$zonelen = 3-$x
		$zone = ""
		$shortIp = ""

		while ( $zonelen -ne 0 ) {
		   $zone = $zone + $octets[$zonelen-1] + "."
		   $zonelen = $zonelen-1
		}

		$y = 0;

		while ( $y -lt $x+1   ) {
		   $shortIp = $shortIp+$revoctets[$y]+"."
		   $y=$y+1
		}
		$shortIp=$shortIp.TrimEnd(".")

		$zone=$zone + "in-addr.arpa"
		Write-Host $shortIp - $zone
		$check = Get-DnsServerZone -ComputerName $dnsServer -Name $zone -ErrorAction SilentlyContinue
		if ( $check -ne $null ){
		   Write-Host "Found Reverse Zone $zone"
		   Write-Host "ZONE: $zone   SHORTIP: $shortIp"
		   $reverseZone=$zone;
		   break;
		}
	  $x=$x+1

	}

	if ( $reverseZone -eq "" ) {
	  $errorStr = "Unable to Find Reverese Zone for Hostname $Hostname IP $ip"
	}

}

if ( $releaseARecord -eq $true ) {
	$check = Get-DnsServerZone -ComputerName $dnsServer -Name $domain -ErrorAction SilentlyContinue
	if ( $check -eq $null ){
	   $errorStr =  "$errorStr`r`nDid not find Zone $domain in DNS Server $dnsServer"
	} else {
	   Write-Host "Found domain $domain in DNS Server $dnsServer"
	}
}

# Exit if we can't find the Reverse or Forward Zones
if ( $errorStr -ne "" ) {
  Write-StdErr "ERROR: $errorStr"
  exit 2
}


# Remove Records
$errorStr = ""
if ( $releasePtrRecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $reverseZone -Name $shortIP -RRType Ptr -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  Try {
		Remove-DnsServerResourceRecord -Force -ComputerName $dnsServer -ZoneName $reverseZone -Name $shortIP -RRType "Ptr" -ErrorAction Stop
	  } Catch {
	  	 echo $_.Exception|format-list -force
		 $ErrMsg = $_.Exception.Message
		 $errorStr = "$errorStr Unable to remove PTR Record. $ErrMsg"
	  }

	  if ( $errorStr -eq "" ) {
	     Write-Host "Removed PTR Record for $shortIP in zone $reverseZone and $hostname."
	   }
    } else {
	   Write-Host "No PTR Record to remove for $shortIP in zone $reverseZone and $hostname."
	}
}

if ( $releaseARecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $domain -Name $shortName -RRType A -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  Try {
		Remove-DnsServerResourceRecord -Force -ComputerName $dnsServer -ZoneName $domain -Name $shortName -RRType "A" -ErrorAction Stop
	  } Catch {
	     echo $_.Exception|format-list -force
		 $ErrMsg = $_.Exception.Message
		 $errorStr = "$errorStr Unable to remove A Record. $ErrMsg"
	  }
	  if ($errorStr -eq "" ) {
	    Write-Host "Removed A Record $shortName in $domain."
	  }
	} else {
	  Write-Host "No A Record to remove for $shortName in $domain."
	}
}

if ( $releaseCNameRecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $domain -Name $name -RRType CName -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  Try {
		Remove-DnsServerResourceRecord -Force -ComputerName $dnsServer -ZoneName $domain -Name $name -RRType "CName" -ErrorAction Stop
	  } Catch {
	     echo $_.Exception|format-list -force
		 $ErrMsg = $_.Exception.Message
		 $errorStr = "$errorStr Unable to remove CName Record. $ErrMsg"
	  }
	  if ($errorStr -eq "" ) {
	    Write-Host "Removed CName Record $name in $domain."
	  }
	} else {
	  Write-Host "No CName Record to remove for $name in $domain."
	}
}

if ($errorStr -ne "") {
  Write-StdErr "ERROR: $errorStr  Exiting."
  exit 3
}
