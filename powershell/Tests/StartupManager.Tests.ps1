<#
.SYNOPSIS
    Pester tests for StartupManager module
#>

BeforeAll {
    # Import required modules
    Import-Module "$PSScriptRoot/../SystemTools/Safety.psm1" -Force
    Import-Module "$PSScriptRoot/../SystemTools/Base.psm1" -Force
    Import-Module "$PSScriptRoot/../SystemTools/StartupManager.psm1" -Force
}

Describe "StartupManager Module Tests" {
    Context "StartupItem Class" {
        It "Should create StartupItem with required properties" {
            $item = [StartupItem]::new(
                "TestApp",
                "C:\test.exe",
                [StartupLocation]::REGISTRY_HKCU_RUN,
                $true
            )
            
            $item.Name | Should -Be "TestApp"
            $item.Command | Should -Be "C:\test.exe"
            $item.Location | Should -Be ([StartupLocation]::REGISTRY_HKCU_RUN)
            $item.Enabled | Should -Be $true
        }
        
        It "Should have proper ToString method" {
            $item = [StartupItem]::new(
                "TestApp",
                "C:\test.exe",
                [StartupLocation]::REGISTRY_HKCU_RUN,
                $true
            )
            
            $string = $item.ToString()
            $string | Should -Match "TestApp"
            $string | Should -Match "✓"
        }
    }
    
    Context "StartupManager Class - Basic" {
        It "Should create StartupManager instance" {
            $manager = [StartupManager]::new()
            
            $manager | Should -Not -BeNullOrEmpty
            $manager.DryRun | Should -Be $false
        }
        
        It "Should create in dry-run mode" {
            $manager = [StartupManager]::new(@{}, $true)
            
            $manager.DryRun | Should -Be $true
        }
        
        It "Should get metadata" {
            $manager = [StartupManager]::new()
            $metadata = $manager.GetMetadata()
            
            $metadata.Name | Should -Be "Startup Manager"
            $metadata.Version | Should -Be "0.3.0"
            $metadata.Category | Should -Be "performance"
        }
    }
    
    Context "StartupManager - List Operations" {
        BeforeAll {
            $script:manager = [StartupManager]::new()
        }
        
        It "Should list startup items without errors" {
            { $script:items = $script:manager.ListStartupItems() } | Should -Not -Throw
        }
        
        It "Should return array of startup items" {
            $items = $script:manager.ListStartupItems()
            
            $items | Should -BeOfType [array]
        }
        
        It "Should get boot time estimate" {
            $bootTime = $script:manager.GetBootTimeEstimate()
            
            $bootTime | Should -BeOfType [double]
            $bootTime | Should -BeGreaterThan 0
        }
        
        It "Should get recommendations" {
            $recommendations = $script:manager.GetRecommendations()
            
            $recommendations | Should -BeOfType [array]
        }
    }
    
    Context "StartupManager - Dry Run Operations" {
        BeforeAll {
            $script:dryManager = [StartupManager]::new(@{}, $true)
            $script:testItem = [StartupItem]::new(
                "TestApp",
                "C:\test.exe",
                [StartupLocation]::REGISTRY_HKCU_RUN,
                $true
            )
        }
        
        It "Should disable item in dry run" {
            { $result = $script:dryManager.DisableStartupItem($script:testItem) } | Should -Not -Throw
        }
        
        It "Should enable item in dry run" {
            $disabledItem = [StartupItem]::new(
                "TestApp",
                "C:\test.exe",
                [StartupLocation]::REGISTRY_HKCU_RUN,
                $false
            )
            
            { $result = $script:dryManager.EnableStartupItem($disabledItem) } | Should -Not -Throw
        }
        
        It "Should remove item in dry run" {
            { $result = $script:dryManager.RemoveStartupItem($script:testItem) } | Should -Not -Throw
        }
    }
    
    Context "StartupManager - Helper Methods" {
        BeforeAll {
            $script:manager = [StartupManager]::new()
        }
        
        It "Should get registry path for location" {
            $path = $script:manager.GetRegistryPath([StartupLocation]::REGISTRY_HKCU_RUN)
            
            $path | Should -Not -BeNullOrEmpty
            $path | Should -BeLike "*HKCU:*"
            $path | Should -BeLike "*Run*"
        }
        
        It "Should handle different startup locations" {
            $locations = @(
                [StartupLocation]::REGISTRY_HKLM_RUN,
                [StartupLocation]::REGISTRY_HKCU_RUN,
                [StartupLocation]::REGISTRY_HKLM_RUN_ONCE,
                [StartupLocation]::REGISTRY_HKCU_RUN_ONCE
            )
            
            foreach ($location in $locations) {
                $path = $script:manager.GetRegistryPath($location)
                $path | Should -Not -BeNullOrEmpty
            }
        }
    }
    
    Context "Convenience Functions" {
        It "Should get startup items via function" {
            { $items = Get-StartupItems } | Should -Not -Throw
        }
        
        It "Should handle disable with mock item" {
            Mock Get-StartupItems { 
                return @([StartupItem]::new("Test", "C:\test.exe", [StartupLocation]::REGISTRY_HKCU_RUN, $true))
            } -ModuleName StartupManager
            
            # This will fail in actual execution but tests the function exists
            { Disable-StartupItem -Name "NonExistent" -ErrorAction Stop } | Should -Throw
        }
    }
}

Describe "StartupManager Integration Tests" {
    Context "End-to-End Workflow" {
        It "Should complete full dry-run workflow" {
            $manager = [StartupManager]::new(@{}, $true)
            
            # List items
            $items = $manager.ListStartupItems()
            $items | Should -BeOfType [array]
            
            # Get estimates
            $bootTime = $manager.GetBootTimeEstimate()
            $bootTime | Should -BeGreaterOrEqual 0
            
            # Get recommendations
            $recommendations = $manager.GetRecommendations()
            $recommendations | Should -BeOfType [array]
            
            # Test operations on mock item
            $testItem = [StartupItem]::new(
                "TestApp",
                "C:\test.exe",
                [StartupLocation]::REGISTRY_HKCU_RUN,
                $true
            )
            
            $result = $manager.DisableStartupItem($testItem)
            $result | Should -Be $true
        }
    }
}
