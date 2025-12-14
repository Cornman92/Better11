$publicFunctions = Get-ChildItem -Path "$PSScriptRoot\Functions\Public\*.ps1"
foreach ($function in $publicFunctions) {
    . $function.FullName
}

Export-ModuleMember -Function @(
    'Get-Better11Apps',
    'Install-Better11App',
    'Uninstall-Better11App',
    'Get-Better11AppStatus'
)
