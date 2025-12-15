#Requires -Modules @{ ModuleName="Pester"; ModuleVersion="5.0.0" }

BeforeAll {
    # Import the Better11 module
    $ModulePath = Join-Path $PSScriptRoot '..' 'Better11.psd1'
    Import-Module $ModulePath -Force
}

Describe 'Get-Better11Apps' {
    It 'Should return array of applications' {
        $apps = Get-Better11Apps
        $apps | Should -Not -BeNullOrEmpty
        $apps | Should -BeOfType [PSCustomObject]
    }
    
    It 'Should have required properties' {
        $apps = Get-Better11Apps | Select-Object -First 1
        $apps.PSObject.Properties.Name | Should -Contain 'AppId'
        $apps.PSObject.Properties.Name | Should -Contain 'Name'
        $apps.PSObject.Properties.Name | Should -Contain 'Version'
        $apps.PSObject.Properties.Name | Should -Contain 'InstallerType'
    }
    
    It 'Should filter by installed when -Installed is specified' {
        $installedApps = Get-Better11Apps -Installed
        $installedApps | ForEach-Object {
            $_.Installed | Should -Be $true
        }
    }
}

Describe 'Install-Better11App' {
    It 'Should accept AppId parameter' {
        { Install-Better11App -AppId 'demo-app' -DryRun } | Should -Not -Throw
    }
    
    It 'Should return result object in dry-run mode' {
        $result = Install-Better11App -AppId 'demo-app' -DryRun -Force
        $result | Should -Not -BeNullOrEmpty
        $result.PSObject.Properties.Name | Should -Contain 'Status'
        $result.Status | Should -Be 'DryRun'
    }
    
    It 'Should throw when app not found' {
        { Install-Better11App -AppId 'nonexistent-app' -Force -ErrorAction Stop } | 
            Should -Throw
    }
}

Describe 'Common Functions' {
    Context 'Test-Better11Administrator' {
        It 'Should return boolean value' {
            $result = Test-Better11Administrator
            $result | Should -BeOfType [bool]
        }
    }
    
    Context 'Write-Better11Log' {
        It 'Should not throw with valid parameters' {
            { Write-Better11Log -Message 'Test message' -Level Info } | Should -Not -Throw
        }
        
        It 'Should create log file' {
            Write-Better11Log -Message 'Test log entry' -Level Info
            $logPath = Join-Path $env:USERPROFILE '.better11\logs\better11.log'
            Test-Path $logPath | Should -Be $true
        }
    }
}

Describe 'Security Functions' {
    Context 'Verify-Better11FileHash' {
        It 'Should verify hash correctly' {
            # Create a test file
            $testFile = Join-Path $TestDrive 'test.txt'
            'Test content' | Out-File -FilePath $testFile -Encoding utf8
            
            # Calculate hash
            $hash = (Get-FileHash -Path $testFile -Algorithm SHA256).Hash
            
            # Verify
            $result = Verify-Better11FileHash -FilePath $testFile -ExpectedHash $hash
            $result.IsMatch | Should -Be $true
        }
        
        It 'Should detect hash mismatch' {
            $testFile = Join-Path $TestDrive 'test2.txt'
            'Different content' | Out-File -FilePath $testFile -Encoding utf8
            
            $wrongHash = 'abc123'
            $result = Verify-Better11FileHash -FilePath $testFile -ExpectedHash $wrongHash
            $result.IsMatch | Should -Be $false
        }
    }
}

AfterAll {
    # Clean up
    Remove-Module Better11 -ErrorAction SilentlyContinue
}
