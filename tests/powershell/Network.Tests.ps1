$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$sut = (Split-Path -Leaf $MyInvocation.MyCommand.Path) -replace '\.Tests\.ps1$', '.psm1'
$modulePath = "$here/../../powershell/Better11/Modules/Network/Network.psd1"

Describe "Better11 Network Module" {
    BeforeAll {
        Import-Module $modulePath -Force
    }

    Context "Get-Better11NetworkAdapters" {
        It "Should return network adapters" {
            $adapters = Get-Better11NetworkAdapters
            $adapters | Should -Not -BeNullOrEmpty
        }

        It "Should filter physical adapters if requested" {
            # Mocking Get-NetAdapter might be needed for robust testing
            # For now just checking command availability
            { Get-Better11NetworkAdapters -PhysicalOnly } | Should -Not -Throw
        }
    }

    Context "Test-Better11NetworkConnectivity" {
        It "Should test connectivity to default targets" {
            # Mocking Test-Connection to avoid actual network calls during CI
            Mock Test-Connection { return $true }
            
            $result = Test-Better11NetworkConnectivity
            $result | Should -Not -BeNullOrEmpty
            $result.Status | Should -Contain "Success"
        }
    }
}
