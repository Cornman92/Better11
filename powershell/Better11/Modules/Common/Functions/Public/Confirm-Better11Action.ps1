function Confirm-Better11Action {
    <#
    .SYNOPSIS
        Prompts the user to confirm an action.
    
    .DESCRIPTION
        Displays a confirmation prompt and returns true if user confirms.
        Logs the user's decision for audit purposes.
    
    .PARAMETER Prompt
        The prompt message to display to the user.
    
    .PARAMETER DefaultYes
        If specified, defaults to Yes when user presses Enter without input.
    
    .EXAMPLE
        if (Confirm-Better11Action "Delete temporary files?") {
            Remove-Item $tempFiles
        }
    
    .EXAMPLE
        $confirmed = Confirm-Better11Action -Prompt "Apply registry tweaks?" -DefaultYes
    
    .OUTPUTS
        Boolean
        Returns $true if user confirmed, $false otherwise.
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Prompt,
        
        [Parameter()]
        [switch]$DefaultYes
    )
    
    begin {
        $choice = if ($DefaultYes) { 'Y/n' } else { 'y/N' }
    }
    
    process {
        Write-Host -NoNewline -ForegroundColor Yellow "$Prompt [$choice]: "
        $response = Read-Host
        
        if ([string]::IsNullOrWhiteSpace($response)) {
            $confirmed = $DefaultYes.IsPresent
        }
        else {
            $confirmed = $response -match '^[yY]'
        }
        
        if ($confirmed) {
            Write-Better11Log -Message "User confirmed: $Prompt" -Level 'Info'
        }
        else {
            Write-Better11Log -Message "User declined: $Prompt" -Level 'Warning'
        }
        
        return $confirmed
    }
}
