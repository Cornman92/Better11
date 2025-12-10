BeforeAll {
    # Import the Better11 module
    $ModulePath = Join-Path $PSScriptRoot '..\Better11.psd1'
    Import-Module $ModulePath -Force
}

Describe 'Performance Module Tests' {
    Context 'Get-Better11SystemInfo' {
        It 'Should return system information' {
            $Result = Get-Better11SystemInfo
            $Result | Should -Not -BeNullOrEmpty
            $Result.ComputerName | Should -Not -BeNullOrEmpty
            $Result.OSName | Should -Not -BeNullOrEmpty
            $Result.TotalMemoryGB | Should -BeGreaterThan 0
        }
    }

    Context 'Get-Better11PerformanceMetrics' {
        It 'Should return performance metrics' {
            $Result = Get-Better11PerformanceMetrics
            $Result | Should -Not -BeNullOrEmpty
            $Result.CPUUsagePercent | Should -BeGreaterOrEqual 0
            $Result.MemoryUsagePercent | Should -BeGreaterOrEqual 0
        }
    }

    Context 'Test-Better11SystemHealth' {
        It 'Should perform health check' {
            $Result = Test-Better11SystemHealth
            $Result | Should -Not -BeNullOrEmpty
            $Result.OverallStatus | Should -BeIn @('Healthy', 'Warning', 'Critical')
            $Result.Checks | Should -Not -BeNullOrEmpty
        }
    }

    Context 'Get-Better11StartupImpact' {
        It 'Should return startup items' {
            $Result = Get-Better11StartupImpact
            $Result | Should -Not -BeNullOrEmpty
        }
    }
}

Describe 'Backup Module Tests' {
    Context 'New-Better11Backup' {
        It 'Should create a backup' {
            $Result = New-Better11Backup -Description "Test backup" -WhatIf
            # WhatIf should not create actual backup
        }
    }

    Context 'Get-Better11BackupList' {
        It 'Should return backup list' {
            $Result = Get-Better11BackupList
            $Result | Should -BeOfType [System.Array]
        }
    }
}

Describe 'Network Module Tests' {
    Context 'Get-Better11NetworkInfo' {
        It 'Should return network information' {
            $Result = Get-Better11NetworkInfo
            $Result | Should -Not -BeNullOrEmpty
            $Result[0].Name | Should -Not -BeNullOrEmpty
        }
    }

    Context 'Test-Better11NetworkSpeed' {
        It 'Should test network speed' {
            $Result = Test-Better11NetworkSpeed -TestHosts @('8.8.8.8')
            $Result | Should -Not -BeNullOrEmpty
            $Result[0].Host | Should -Be '8.8.8.8'
        }
    }

    Context 'Get-Better11ActiveConnections' {
        It 'Should return active connections' {
            $Result = Get-Better11ActiveConnections -Protocol TCP
            $Result | Should -Not -BeNullOrEmpty
        }
    }
}

AfterAll {
    Remove-Module Better11 -Force -ErrorAction SilentlyContinue
}
