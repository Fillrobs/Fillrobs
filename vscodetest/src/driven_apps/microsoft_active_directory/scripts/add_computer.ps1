  Import-Module ActiveDirectory
$CreateOU = {{create_ou}}
$RemoveBuildOU = {{remove_build_ou}}
#if MoveOU is true then this is a move and not just an add
$MoveOU = {{move_ou}}
$Domain = "{{domain}}"
$Description = ""
$ComputerName = "{{computer_name}}"
$OU="{{ou}}"
$BuildOU="{{build_ou}}"
$SecurityGroups=New-Object System.Collections.ArrayList


{% for group in security_group_designated_names %}
$SecurityGroups.Add("{{group}}")
{% endfor %}

$Server = "{{server}}"

if ($MoveOU -eq $true){
    $FullComputerName = "CN=$ComputerName,$BuildOU"
} else {
    $FullComputerName = "CN=$ComputerName,$OU"
}
Function OuExists{
    Param($Group)
    try{
        Get-ADOrganizationalUnit $Group -Server $Server
    }
    catch{
        return $false;
    }
	return $true
}
Function CreateOUWithParents {
	Param($DN)
	# A regex to split the DN, taking escaped commas into account
	$DNRegex = '(?<![\\]),'
	# We'll need to traverse the path, level by level, let's figure out the number of possible levels
	$Depth = ($DN -split $DNRegex).Count
	# Step through each possible parent OU
	for($i = 1;$i -le $Depth;$i++)
	{
		$NextOU = ($DN -split $DNRegex,$i)[-1]
		if($NextOU.IndexOf("OU=",[StringComparison]"CurrentCultureIgnoreCase") -ne 0 -or (OuExists($NextOU)))
		{
			break
		}
		else
		{
			# OU does not exist, remember this for later
			[String[]]$MissingOUs += $NextOU
		}
	}
	# Reverse the order of missing OUs, we want to create the top-most needed level first
	[array]::Reverse($MissingOUs)
	# Now create the missing part of the tree, including the desired OU
	foreach($OU in $MissingOUs)
	{
		$newOUName = (($OU -split $DNRegex,2)[0] -split "=")[1]
		$newOUPath = ($OU -split $DNRegex,2)[1]
		New-ADOrganizationalUnit -Name $newOUName -Path $newOUPath -Server $Server
	}
}
Function RemoveOUWithEmptyParents {
	Param($DN)
	# A regex to split the DN, taking escaped commas into account
	$DNRegex = '(?<![\\]),'
	# We'll need to traverse the path, level by level, let's figure out the number of possible levels
	$Depth = ($DN -split $DNRegex).Count
	# Step through each possible parent OU
	for($i = 1;$i -le $Depth;$i++) {
		$NextOU = ($DN -split $DNRegex,$i)[-1]
		if($NextOU.IndexOf("OU=") -ne -1 -and (OuExists($NextOU))) {
			$objs = Get-ADObject -Filter * -SearchBase $NextOU -Server $Server
			if ( @($objs).length -eq 1) {
				Write-Host "Removing empty $NextOU"
				Try {
					set-ADOrganizationalUnit -Identity $NextOU -ProtectedFromAccidentalDeletion $false -Server $Server
					Remove-ADOrganizationalUnit -Identity $NextOU -Confirm:$False -Server $Server
				} Catch {
					Write-Host "ERROR: Failed to remove $NextOU"
					Write-Host $_.Exception.Message
				}
			} else {
				Write-Host "OU $NextOU is not empty, not removing."
			    break
			}
		}
	}
}
if ( $OU -ne "" ) {
	# Create OU if it does not exists
	try {
		$exists=OuExists $OU
		if (( $exists -eq $false ) -and ( $CreateOU -eq $true )) {
			Write-Host "Creating OU $OU"
			CreateOUWithParents($OU)
			$exists = $true
		}
	} catch {
	        $ErrMsg = $_.Exception.Message
			Write-Host "ERROR: Creating $OU failed: $ErrMsg"
			exit 1
	}
	# If it's a MOVE then we behave differently than if it's an ADD
	if ($MoveOU -eq $true ){
		try {
			get-adcomputer -Identity $FullComputerName -Server $Server | Move-ADObject -Server $Server -TargetPath $OU
		} catch {
            $ErrMsg = $_.Exception.Message
			Write-Host "ERROR: MOVING $FullComputerName failed: $ErrMsg"
			exit 1
		}
		try {
			$exists=OuExists $BuildOU
			if (( $exists -eq $true ) -and ( $RemoveBuildOU -eq $true )) {
				Write-Host "DELETING OU $BuildOU"
				RemoveOUWithEmptyParents($BuildOU)
				$exists = $true
			}
		} catch {
			Write-Host "ERROR: Removing $BuildOU failed"
			exit 1
		}
	} else {
        Try {
            if ($exists -eq $true ) {
                Write-Host "Adding Computer $ComputerName to OU $OU"
                New-ADComputer -Name $ComputerName -SamAccountName $ComputerName -Path $OU -Description $Description -Enabled $true -Server $Server
            } else {
                Write-Host "ERROR:  OU $OU does not exist and CreateOU is not enabled.  Exiting."
                exit 1
            }
        } Catch {
            Write-Host "ERROR: Failed to add Computer $ComputerName"
            Write-Host $_.Exception.Message
            $err = $true;
        }
	}
}
if ($MoveOU -ne $true ){
    if ( $SecurityGroups -ne "" ) {
        $err = $false;
        foreach ($SG in @($SecurityGroups)) {
            Try {
                Write-Host "Adding Computer $FullComputerName to $SG"
                Add-ADGroupMember $SG -Members $FullComputerName -Server $Server
            } Catch {
                Write-Host "ERROR: Failed to add Computer $ComputerName to Security Group $SG"
                Write-Host $_.Exception.Message
                $err = $true;
            }
        }
        #If error, remove them from the Security Groups
        if ( $err -eq $true ) {
            foreach ($SG in $SecurityGroups) {
                Try {
                    Write-Host "$FullComputerName"
                    Write-Host "Removing $ComputerName from $SG"
                    Remove-ADGroupMember $SG -Members $FullComputerName -Confirm:$false -Server $Server
                } Catch {
                    $err = $true;
                }
            }
            exit 5;
        }
    }
}
