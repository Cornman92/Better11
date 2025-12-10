function Confirm-Better11Action {
    <#
    .SYNOPSIS
        Prompts the user to confirm an action.
    
    .DESCRIPTION
        Displays a confirmation prompt to the user and returns true if they confirm,
        false if they decline. Supports default responses and custom messages.
    
    .PARAMETER Message
        The confirmation message to display
    
    .PARAMETER DefaultYes
        If specified, defaults to Yes on Enter
    
    .PARAMETER Force
        If specified, skips confirmation and returns true
    
    .EXAMPLE
        if (Confirm-Better11Action "Delete temporary files?") {
            # Proceed with deletion
        }
    
    .EXAMPLE
        Confirm-Better11Action "Install application?" -DefaultYes
    
    .OUTPUTS
        Boolean
        True if user confirmed, False if declined
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message,
        
        [Parameter()]
        [switch]$DefaultYes,
        
        [Parameter()]
        [switch]$Force
    )
    
    process {
        # Skip confirmation if Force is specified
        if ($Force) {
            Write-Better11Log -Message "Confirmation bypassed with -Force: $Message" -Level Debug
            return $true
        }
        
        # Build prompt
        $prompt = if ($DefaultYes) { "[Y/n]" } else { "[y/N]" }
        $fullPrompt = "$Message $prompt"
        
        # Get user input
        $response = Read-Host -Prompt $fullPrompt
        
        # Handle empty response (Enter key)
        if ([string]::IsNullOrWhiteSpace($response)) {
            $confirmed = $DefaultYes.IsPresent
        }
        else {
            $confirmed = $response -match '^[yY]'
        }
        
        # Log result
        $resultText = if ($confirmed) { "confirmed" } else { "declined" }
        Write-Better11Log -Message "User $resultText action: $Message" -Level Info
        
        return $confirmed
    }
}
