   Import-Module ActiveDirectory
$RemoveOU = {{remove_ou}}
$removeAllADHostBySAM = {{delete_computer_accounts_by_name}}
$Domain = ""
$ComputerName = "{{computer_name}}"
$OU="{{ou}}"
$Server="{{server}}"
#fix issues with scripting.log and special variable names. Use these for write-host.
$LogCompName=$ComputerName
$LogServer=$Server
Function OuExists{
	Param($Group)
	Try {
		Get-ADOrganizationalUnit $Group -Server $Server
	} catch {
		return $false;
	}
	return $true
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
Function EvaluateGetADErrorMessage {
	param($errorMsg)
	$errStrParse=$errorMsg|select-string  -pattern "Unable to contact the server"
	if ($errStrParse.length -gt 0) {
		return 3
	} elseif ($errStrParse=$errorMsg|select-string  -pattern "Cannot find an object with identity") {
		if ($errStr.length -gt 0) {
			return 9
		}
	} else {
		return 1
	}
}
Function EvaluateRemoveADErrorMessage {
	param($errorMsg)
	$errStrParse=$errorMsg|select-string  -pattern "error, failure, failed, unable"
	if ($errStrParse.length -gt 0) {
		return 1
	} elseif ($errStrParse=$errorMsg|select-string  -pattern "transient") {
		if ($errStr.length -gt 0) {
			#A connection to the directory on which to process the request was unavailable. This is likely a transient condition.
			return 9
		}
	} else {
		return 1
	}
}
if( $removeAllADHostBySAM -eq $true ){
	Write-Host "Looking up $LogCompName in AD server $LogServer"
	try {
		$compObj=get-adcomputer -Identity $ComputerName -Server $Server
	} catch {
		$errStr = $_.Exception.Message
		switch (EvaluateGetADErrorMessage $errStr) {
			1 { Write-Host "ERROR: Unable to look up $LogCompName in $LogServer."; exit 1}
			3 { Write-Host "ERROR: Unable to connect to AD server $LogServer. Exiting"; exit 1	}
			9 { Write-Host "WARNING: Could not find a Computer with name $LogCompName in $LogServer"; exit 0 }
			default { Write-Host "Unexpected response looking up $LogCompName" ; exit 1}
		}
	}
	try {
		for ( $count=1; $count -le 5; $count++ ){
			Write-Host "Removing $LogCompName from AD, attempt number $count..."
			$compObj|Remove-ADObject -Server $Server -Confirm:$false
			$ADRet = $?
			if ($ADRet -eq "True") {
				Write-Host "Successfully removed $LogCompName from AD"
				break
			} else {
				$sleepTime = Get-Random -Minimum 10 -Maximum 40
				Write-Host "AD computer remove failed.  Sleeping $sleepTime seconds before retry."
				Start-Sleep $sleepTime
			}
		}
	} catch {
		Write-Host "ERROR removing $LogCompName failed. All retries failed."
		Write-Host $_.Exception.Message
		exit 1
	}
} else {
	if ( $OU -ne "" ) {
		#Verify object exists
		try {
			$compObj=get-adcomputer -Filter 'Name -eq $ComputerName' -SearchBase "$OU"  -Server $Server
			if ($compObj.Name -ne $ComputerName){
				write-host "Could not find $LogCompName in AD"
				exit 0
			}
		} catch {
			write-host "** error from AD is $errStr"
			switch (EvaluateGetADErrorMessage $errStr) {
				1 { Write-Host "ERROR: Unable to look up $LogCompName in $LogServer."; exit 1}
				3 { Write-Host "ERROR: Unable to connect to AD server $LogServer. Exiting"; exit 1}
				default { Write-Host "Unexpected response looking up $LogCompName" ; exit 1}
			}
		}
		Try {
			for ( $count=1; $count -le 5; $count++){
				Write-Host "Removing computer $LogCompName from $OU, attempt number $count"
				$compObj|Remove-ADComputer -confirm:$false -Server $Server
				$ADRet = $?
				if ($ADRet -eq "True") {
					Write-Host "Removed Computer $LogCompName from $OU"
					break
				} else {
					$sleepTime = Get-Random -Minimum 10 -Maximum 40
					Write-Host "AD computer remove failed.  Sleeping $sleepTime seconds before retry."
					Start-Sleep $sleepTime
					$errStr = $_.Exception.Message
					switch (EvaluateRemoveADErrorMessage $errStr) {
						1 { Write-Host "ERROR: Unable to remove $LogCompName in $LogServer"}
						9 { Write-Host "WARNING: AD reported a transient error removing $LogCompName from $LogServer" }
						default { Write-Host "Unexpected response removing AD entry $LogCompName in $LogServer" ; exit 1}
					}
				}
			}
		} Catch {
			Write-Host "ERROR: Failed to remove Computer $LogCompName from $OU"
			Write-Host $_.Exception.Message
			exit 1
		}
	}
}
# Remove OU if it exists and is empty
$exists=OuExists $OU
if (( $exists -eq $true ) -and ( $RemoveOU -eq $true )) {
	RemoveOUWithEmptyParents($OU)
	$exists = $true
}
