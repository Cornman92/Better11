using System;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for managing privacy and telemetry settings.
    /// </summary>
    public class PrivacyService : IPrivacyService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<PrivacyService> _logger;

        public PrivacyService(PowerShellExecutor psExecutor, ILogger<PrivacyService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<PrivacyStatus> GetPrivacyStatusAsync()
        {
            try
            {
                _logger.LogInformation("Getting privacy status");

                var telemetry = await GetTelemetryLevelAsync();
                
                // Check Cortana status
                var cortanaResult = await _psExecutor.ExecuteCommandAsync(@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search'
                    $value = Get-ItemProperty -Path $path -Name 'CortanaConsent' -ErrorAction SilentlyContinue
                    if ($value) { $value.CortanaConsent -eq 1 } else { $true }
                ");
                var cortanaEnabled = cortanaResult.Output.Count > 0 && 
                    cortanaResult.Output[0]?.ToString()?.ToLower() == "true";

                // Check Location status
                var locationResult = await _psExecutor.ExecuteCommandAsync(@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location'
                    $value = Get-ItemProperty -Path $path -Name 'Value' -ErrorAction SilentlyContinue
                    if ($value) { $value.Value -eq 'Allow' } else { $true }
                ");
                var locationEnabled = locationResult.Output.Count > 0 && 
                    locationResult.Output[0]?.ToString()?.ToLower() == "true";

                // Check Advertising ID status
                var adIdResult = await _psExecutor.ExecuteCommandAsync(@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
                    $value = Get-ItemProperty -Path $path -Name 'Enabled' -ErrorAction SilentlyContinue
                    if ($value) { $value.Enabled -eq 1 } else { $true }
                ");
                var adIdEnabled = adIdResult.Output.Count > 0 && 
                    adIdResult.Output[0]?.ToString()?.ToLower() == "true";

                // Check Activity History status
                var activityResult = await _psExecutor.ExecuteCommandAsync(@"
                    $path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System'
                    $value = Get-ItemProperty -Path $path -Name 'EnableActivityFeed' -ErrorAction SilentlyContinue
                    if ($value) { $value.EnableActivityFeed -eq 1 } else { $true }
                ");
                var activityEnabled = activityResult.Output.Count > 0 && 
                    activityResult.Output[0]?.ToString()?.ToLower() == "true";

                return new PrivacyStatus
                {
                    TelemetryLevel = telemetry,
                    CortanaEnabled = cortanaEnabled,
                    LocationEnabled = locationEnabled,
                    AdvertisingIdEnabled = adIdEnabled,
                    ActivityHistoryEnabled = activityEnabled
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get privacy status");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<TelemetryLevel> GetTelemetryLevelAsync()
        {
            try
            {
                _logger.LogInformation("Getting telemetry level");

                var result = await _psExecutor.ExecuteCommandAsync(@"
                    $path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
                    $value = Get-ItemProperty -Path $path -Name 'AllowTelemetry' -ErrorAction SilentlyContinue
                    if ($value) { $value.AllowTelemetry } else { 3 }
                ");

                if (result.Success && result.Output.Count > 0)
                {
                    if (int.TryParse(result.Output[0]?.ToString(), out var level))
                    {
                        return (TelemetryLevel)Math.Clamp(level, 0, 3);
                    }
                }

                return TelemetryLevel.Full;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get telemetry level");
                return TelemetryLevel.Full;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetTelemetryLevelAsync(TelemetryLevel level)
        {
            try
            {
                _logger.LogInformation("Setting telemetry level to {Level}", level);

                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
                    if (-not (Test-Path $path)) {{
                        New-Item -Path $path -Force | Out-Null
                    }}
                    Set-ItemProperty -Path $path -Name 'AllowTelemetry' -Value {(int)level} -Type DWord
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set telemetry level");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetCortanaEnabledAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} Cortana", enabled ? "Enabling" : "Disabling");

                var value = enabled ? 1 : 0;
                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search'
                    if (-not (Test-Path $path)) {{
                        New-Item -Path $path -Force | Out-Null
                    }}
                    Set-ItemProperty -Path $path -Name 'CortanaConsent' -Value {value} -Type DWord
                    Set-ItemProperty -Path $path -Name 'AllowCortana' -Value {value} -Type DWord
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Cortana status");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetLocationEnabledAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} location services", enabled ? "Enabling" : "Disabling");

                var value = enabled ? "Allow" : "Deny";
                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location'
                    if (-not (Test-Path $path)) {{
                        New-Item -Path $path -Force | Out-Null
                    }}
                    Set-ItemProperty -Path $path -Name 'Value' -Value '{value}'
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set location status");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetAdvertisingIdEnabledAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} advertising ID", enabled ? "Enabling" : "Disabling");

                var value = enabled ? 1 : 0;
                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
                    if (-not (Test-Path $path)) {{
                        New-Item -Path $path -Force | Out-Null
                    }}
                    Set-ItemProperty -Path $path -Name 'Enabled' -Value {value} -Type DWord
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set advertising ID status");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetActivityHistoryEnabledAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} activity history", enabled ? "Enabling" : "Disabling");

                var value = enabled ? 1 : 0;
                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System'
                    if (-not (Test-Path $path)) {{
                        New-Item -Path $path -Force | Out-Null
                    }}
                    Set-ItemProperty -Path $path -Name 'EnableActivityFeed' -Value {value} -Type DWord
                    Set-ItemProperty -Path $path -Name 'PublishUserActivities' -Value {value} -Type DWord
                    Set-ItemProperty -Path $path -Name 'UploadUserActivities' -Value {value} -Type DWord
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set activity history status");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ApplyRecommendedSettingsAsync()
        {
            try
            {
                _logger.LogInformation("Applying recommended privacy settings");

                var success = true;
                success &= await SetTelemetryLevelAsync(TelemetryLevel.Basic);
                success &= await SetCortanaEnabledAsync(false);
                success &= await SetAdvertisingIdEnabledAsync(false);
                success &= await SetActivityHistoryEnabledAsync(false);

                _logger.LogInformation("Recommended privacy settings applied: {Success}", success);
                return success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply recommended privacy settings");
                return false;
            }
        }
    }
}
