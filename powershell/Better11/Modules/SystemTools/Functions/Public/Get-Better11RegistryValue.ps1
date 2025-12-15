function Get-Better11RegistryValue {
    <#
    .SYNOPSIS
        Gets a registry value.

    .DESCRIPTION
        Retrieves a registry value. Returns $null if not found.

    .PARAMETER Path
        Registry key path.

    .PARAMETER Name
        Value name.

    .EXAMPLE
        Get-Better11RegistryValue -Path "HKCU:\Software\Test" -Name "EnableFeature"
        Gets a value.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,

        [Parameter(Mandatory=$true)]
        [string]$Name
    )

    process {
        try {
            $value = Get-ItemProperty -Path $Path -Name $Name -ErrorAction SilentlyContinue
            if ($value) {
                return $value.$Name
            }
            return $null
        }
        catch {
            Write-Better11Log -Message "Failed to get registry value: $_" -Level "ERROR"
            return $null
        }
    }
}
