#Requires -Version 5.1

# Dot source public functions
$PublicFunctions = Get-ChildItem -Path "$PSScriptRoot\Functions\Public\*.ps1" -ErrorAction SilentlyContinue
foreach ($Function in $PublicFunctions) {
    . $Function.FullName
}

Export-ModuleMember -Function $PublicFunctions.BaseName
