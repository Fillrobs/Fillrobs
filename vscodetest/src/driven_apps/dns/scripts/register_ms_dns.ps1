Import-Module DnsServer
$hostname = "{{hostname}}"
$ip = "{{ip}}"
$name = "{{name}}"
$value = "{{value}}"
$dnsServer = "{{dns_server}}"
$createARecord = {{create_a_record}}
$createPtrRecord = {{create_ptr_record}}
$createCNameRecord = {{create_cname_record}}
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

if ( $createPtrRecord -eq $true ) {
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

if ( $createARecord -eq $true -Or $createCNameRecord -eq $true ) {
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

# Check to make sure there is no conflicting records
$errorStr = ""
if ( $createPtrRecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $reverseZone -Name $shortIP -RRType Ptr -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  $errorStr = "PTR Record already Exists."
	}
}
if ( $createARecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $domain -Name $shortName -RRType A -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  $errorStr = "$errorStr  A Record already Exists."
	}
}
if ( $createCNameRecord -eq $true ) {
	$check = Get-DNSServerResourceRecord -ComputerName $dnsServer -ZoneName $domain -Name $shortName -RRType CName -ErrorAction SilentlyContinue
	if ( $check -ne $null ) {
	  $errorStr = "$errorStr  CName Record already Exists."
	}
}
if ($errorStr -ne "") {
  Write-StdErr "ERROR: $errorStr  Exiting."
  exit 3
}

#Add Records
if ( $createPtrRecord -eq $true) {
   Try {
      add-DnsServerResourceRecordPtr -ComputerName $dnsServer -Name $shortIp -ZoneName $reverseZone -PtrDomainName $hostname -AllowUpdateAny -ErrorAction Stop
   } catch {
      $ErrMsg = $_.Exception.Message
      Write-StdErr "ERROR:  Could not create PTR Record $shortIP in zone $reverseZone for $hostname.  $ErrMsg"
	  exit 4
   }
   Write-Host "Added Ptr Record $shortIP $hostname to zone $reverseZone."
}
if ( $createARecord -eq $true ) {
   Try {
      add-DnsServerResourceRecordA -ComputerName $dnsServer -Name $shortName -ZoneName $domain -AllowUpdateAny -IPv4Address $ip -ErrorAction Stop
   } catch {
      $ErrMsg = $_.Exception.Message
      Write-StdErr "ERROR:  Could not create A Record $shortName in zone $domain.  $ErrMsg"
	  if ( $createPtrRecord -eq $true ) {
	     Write-StdErr "Rolling back PTR Record creation."
		 Try {
		    Remove-DnsServerResourceRecord -Force -ComputerName $dnsServer -ZoneName $reverseZone -Name $shortIP -RRType "Ptr" -ErrorAction Stop
		} catch {
		    $ErrMsg = $_.Exception.Message
			Write-StdErr "Failed rolling back PTR Record $shortIP in $reverseZone for $hostname / $ip.  $ErrMsg"
		}
	  }
	  exit 5
   }
   Write-Host "Added A Record $shortName $ip to zone $domain."
}
if ( $createCNameRecord -eq $true ) {
   Try {
	  add-DnsServerResourceRecordCName -ComputerName $dnsServer -Name $shortName -ZoneName $domain -AllowUpdateAny -HostNameAlias $value -ErrorAction Stop
   } catch {

      $ErrMsg = $_.Exception.Message
	  Write-StdErr "ERROR:  Could not create CName Record $shortName in zone $domain.  $ErrMsg"
	  if ( $createCNameRecord -eq $true ) {
	     Write-StdErr "Rolling back CName Record creation."
		 Try {
		    Remove-DnsServerResourceRecord -Force -ComputerName $dnsServer -ZoneName $reverseZone -Name $value -RRType "CName" -ErrorAction Stop
		} catch {
		    $ErrMsg = $_.Exception.Message
			Write-StdErr "Failed rolling back CName Record $shortName in $reverseZone for $shortName / $value.  $ErrMsg"
		}
	  }
	  exit 5
   }
   Write-Host "Added CName Record $shortName to zone $domain."
}
