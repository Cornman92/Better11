function Set-Better11RegistryValue {
    <#
    .SYNOPSIS
        Sets a registry value.

    .DESCRIPTION
        Sets a registry value, creating the key if it doesn't exist.
        Requires administrative privileges for HKLM.

    .PARAMETER Path
        Registry key path.

    .PARAMETER Name
        Value name.

    .PARAMETER Value
        Value data.

    .PARAMETER Type
        Value type (String, DWord, etc.).

    .EXAMPLE
        Set-Better11RegistryValue -Path "HKCU:\Software\Test" -Name "EnableFeature" -Value 1 -Type DWord
        Sets a DWord value.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,

        [Parameter(Mandatory=$true)]
        [string]$Name,

        [Parameter(Mandatory=$true)]
        [Object]$Value,

        [string]$Type = "String"
    )

    process {
        if ($PSCmdlet.ShouldProcess($Path, "Set Registry Value '$Name' to '$Value'")) {
            Write-Better11Log -Message "Setting registry value $Path\$Name..." -Level "INFO"

            try {
                if (-not (Test-Path $Path)) {
                    New-Item -Path $Path -Force | Out-Null
                }

                New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType $Type -Force | Out-Null
                Write-Better11Log -Message "Registry value set successfully" -Level "SUCCESS"
            }
            catch {
                Write-Better11Log -Message "Failed to set registry value: $_" -Level "ERROR"
                throw
            }
        }
    }
}
