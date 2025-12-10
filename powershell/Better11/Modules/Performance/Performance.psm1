# Load public functions
$PublicFunctions = @(Get-ChildItem -Path "$PSScriptRoot\Functions\Public\*.ps1" -ErrorAction SilentlyContinue)

foreach ($Function in $PublicFunctions) {
    try {
        . $Function.FullName
    }
    catch {
        Write-Error "Failed to import function $($Function.FullName): $_"
    }
}

Export-ModuleMember -Function $PublicFunctions.BaseName
