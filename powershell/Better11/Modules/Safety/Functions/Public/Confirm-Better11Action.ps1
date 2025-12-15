function Confirm-Better11Action {
    <#
    .SYNOPSIS
        Prompts user to confirm a potentially dangerous action.
    .DESCRIPTION
        Displays a confirmation prompt before proceeding with system changes.
    .PARAMETER Message
        The confirmation message to display.
    .PARAMETER Title
        Title for the confirmation dialog.
    .PARAMETER Force
        Skip confirmation and return $true.
    .EXAMPLE
        if (Confirm-Better11Action -Message "Apply privacy settings?") { ... }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter()]
        [string]$Title = "Better11 Confirmation",

        [Parameter()]
        [switch]$Force
    )

    if ($Force) {
        return $true
    }

    $choices = @(
        [System.Management.Automation.Host.ChoiceDescription]::new("&Yes", "Proceed with the action")
        [System.Management.Automation.Host.ChoiceDescription]::new("&No", "Cancel the action")
    )

    $decision = $Host.UI.PromptForChoice($Title, $Message, $choices, 1)
    
    return $decision -eq 0
}
