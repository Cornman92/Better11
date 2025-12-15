<#
.SYNOPSIS
    Pester tests for Better11 Config module
#>

BeforeAll {
    # Import the module
    Import-Module "$PSScriptRoot/../Better11/Config.psm1" -Force
}

Describe "Config Module Tests" {
    Context "LoggingConfig Class" {
        It "Should create with default values" {
            $config = [LoggingConfig]::new()
            
            $config.Level | Should -Be "INFO"
            $config.FileEnabled | Should -Be $true
            $config.ConsoleEnabled | Should -Be $true
            $config.MaxLogSizeMB | Should -Be 10
            $config.BackupCount | Should -Be 5
        }
        
        It "Should create with custom values" {
            $config = [LoggingConfig]::new()
            $config.Level = "DEBUG"
            $config.MaxLogSizeMB = 20
            
            $config.Level | Should -Be "DEBUG"
            $config.MaxLogSizeMB | Should -Be 20
        }
    }
    
    Context "Config Class - Static Methods" {
        It "Should return default path" {
            $path = [Config]::GetDefaultPath()
            
            $path | Should -Not -BeNullOrEmpty
            $path | Should -BeLike "*better11*"
        }
        
        It "Should return system path" {
            $path = [Config]::GetSystemPath()
            
            $path | Should -Not -BeNullOrEmpty
            # On Windows, should be in ProgramData
            if ($IsWindows -or $null -eq $IsWindows) {
                $path | Should -BeLike "*Better11*"
            }
        }
    }
    
    Context "Config Class - Load/Save" {
        BeforeAll {
            $script:testDir = Join-Path $TestDrive "config_tests"
            New-Item -ItemType Directory -Path $script:testDir -Force | Out-Null
        }
        
        It "Should save config to JSON" {
            $config = [Config]::new()
            $testFile = Join-Path $script:testDir "test_config.json"
            
            $config.Save($testFile)
            
            Test-Path $testFile | Should -Be $true
            
            $content = Get-Content $testFile -Raw
            $content | Should -Match "Better11"
            $content | Should -Match "Applications"
        }
        
        It "Should load config from JSON" {
            $testFile = Join-Path $script:testDir "test_load.json"
            
            # Create a test config
            $config1 = [Config]::new()
            $config1.SystemTools.SafetyLevel = "paranoid"
            $config1.Save($testFile)
            
            # Load it back
            $config2 = [Config]::Load($testFile)
            
            $config2.SystemTools.SafetyLevel | Should -Be "paranoid"
        }
        
        It "Should apply environment variable overrides" {
            # Set test environment variable
            $env:BETTER11_AUTO_UPDATE = "false"
            $env:BETTER11_LOG_LEVEL = "DEBUG"
            
            try {
                $config = [Config]::Load()
                $config = [Config]::ApplyEnvOverrides($config)
                
                $config.Better11.AutoUpdate | Should -Be $false
                $config.Logging.Level | Should -Be "DEBUG"
            }
            finally {
                Remove-Item Env:\BETTER11_AUTO_UPDATE -ErrorAction SilentlyContinue
                Remove-Item Env:\BETTER11_LOG_LEVEL -ErrorAction SilentlyContinue
            }
        }
    }
    
    Context "Config Class - Validation" {
        It "Should validate valid config" {
            $config = [Config]::new()
            
            { $config.Validate() } | Should -Not -Throw
        }
        
        It "Should reject invalid safety level" {
            $config = [Config]::new()
            $config.SystemTools.SafetyLevel = "invalid"
            
            { $config.Validate() } | Should -Throw
        }
        
        It "Should reject invalid theme" {
            $config = [Config]::new()
            $config.GUI.Theme = "rainbow"
            
            { $config.Validate() } | Should -Throw
        }
        
        It "Should reject invalid log level" {
            $config = [Config]::new()
            $config.Logging.Level = "VERBOSE"
            
            { $config.Validate() } | Should -Throw
        }
    }
    
    Context "Config Class - ToHashtable" {
        It "Should convert to hashtable" {
            $config = [Config]::new()
            $hash = $config.ToHashtable()
            
            $hash | Should -BeOfType [hashtable]
            $hash.Better11 | Should -Not -BeNullOrEmpty
            $hash.Applications | Should -Not -BeNullOrEmpty
            $hash.SystemTools | Should -Not -BeNullOrEmpty
            $hash.GUI | Should -Not -BeNullOrEmpty
            $hash.Logging | Should -Not -BeNullOrEmpty
        }
    }
    
    Context "Convenience Function" {
        It "Should load config via function" {
            $config = Load-Better11Config
            
            $config | Should -Not -BeNullOrEmpty
            $config.Better11.Version | Should -Be "0.3.0"
        }
    }
}
