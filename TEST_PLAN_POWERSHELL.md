# Better11 - PowerShell Backend Test Plan

## Overview
This document outlines the test plan for the Better11 PowerShell backend modules.

## Modules to Test

### 1. Network Module
- **Get-Better11NetworkAdapters**
  - Verify it lists all adapters
  - Verify physical filter works
- **Reset-Better11TcpIp**
  - Verify it calls netsh (mocked)
  - Verify it requires admin
- **Reset-Better11Winsock**
  - Verify it calls netsh (mocked)
  - Verify it requires admin
- **Test-Better11NetworkConnectivity**
  - Verify it pings targets
  - Verify it returns results object

### 2. Power Module
- **Enable-Better11Hibernation**
  - Verify it calls powercfg /hibernate on
- **Disable-Better11Hibernation**
  - Verify it calls powercfg /hibernate off
- **New-Better11BatteryReport**
  - Verify it generates report at specified path
  - Verify it uses default path if none specified

### 3. Backup Module
- **New-Better11RestorePoint**
  - Verify it calls Checkpoint-Computer
  - Verify description is passed
- **Get-Better11RestorePoints**
  - Verify it calls Get-ComputerRestorePoint
- **Backup-Better11RegistryHive**
  - Verify it calls reg export
  - Verify path handling

### 4. AppManager Module
- **Get-Better11InstalledApps**
  - Verify it reads from Uninstall keys
  - Verify object structure
- **Install-Better11App**
  - Verify it starts installer process
  - Verify arguments passing
- **Uninstall-Better11App**
  - Verify it runs uninstall string

### 5. SystemTools Module
- **Set-Better11RegistryValue**
  - Verify it creates keys/values
  - Verify types (String, DWord)
- **Get-Better11RegistryValue**
  - Verify it reads values
  - Verify $null return on missing
- **Set-Better11ServiceStartMode**
  - Verify it calls Set-Service
  - Verify disabled service is also stopped
- **Remove-Better11Bloatware**
  - Verify it calls Remove-AppxPackage

## Test Execution
Run tests using Pester:

```powershell
Invoke-Pester -Path tests/powershell/
```

## Prerequisite
- PowerShell 5.1 or later
- Pester module installed
- Administrator privileges for integration tests
