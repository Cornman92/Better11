using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for system information gathering.
    /// </summary>
    public class SysInfoService : ISysInfoService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<SysInfoService> _logger;

        public SysInfoService(PowerShellExecutor psExecutor, ILogger<SysInfoService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<SystemSummary> GetSystemSummaryAsync()
        {
            try
            {
                _logger.LogInformation("Getting system summary");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11SystemSummary");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic summary = result.Output[0];
                    return new SystemSummary
                    {
                        ComputerName = summary.ComputerName?.ToString() ?? "",
                        Domain = summary.Domain?.ToString() ?? "",
                        Manufacturer = summary.Manufacturer?.ToString() ?? "",
                        Model = summary.Model?.ToString() ?? "",
                        SystemType = summary.SystemType?.ToString() ?? "",
                        Windows = await GetWindowsInfoAsync(),
                        CPU = await GetCPUInfoAsync(),
                        Memory = await GetMemoryInfoAsync(),
                        GPUs = await GetGPUInfoAsync(),
                        Storage = await GetStorageInfoAsync(),
                        BIOS = await GetBIOSInfoAsync()
                    };
                }

                return new SystemSummary();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get system summary");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<WindowsInfo> GetWindowsInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11WindowsInfo");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic info = result.Output[0];
                    return new WindowsInfo
                    {
                        Version = info.Version?.ToString() ?? "",
                        Build = info.Build?.ToString() ?? "",
                        Edition = info.Edition?.ToString() ?? "",
                        ProductId = info.ProductId?.ToString() ?? "",
                        InstallDate = info.InstallDate ?? DateTime.MinValue,
                        LastBoot = info.LastBoot ?? DateTime.MinValue,
                        UptimeHours = info.UptimeHours ?? 0,
                        RegisteredOwner = info.RegisteredOwner?.ToString() ?? "",
                        SystemRoot = info.SystemRoot?.ToString() ?? "",
                        Architecture = info.Architecture?.ToString() ?? ""
                    };
                }

                return new WindowsInfo();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get Windows info");
                return new WindowsInfo();
            }
        }

        /// <inheritdoc/>
        public async Task<CPUInfo> GetCPUInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11CPUInfo");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic info = result.Output[0];
                    return new CPUInfo
                    {
                        Name = info.Name?.ToString() ?? "",
                        Manufacturer = info.Manufacturer?.ToString() ?? "",
                        Cores = info.Cores ?? 0,
                        LogicalProcessors = info.LogicalProcessors ?? 0,
                        MaxClockMHz = info.MaxClockMHz ?? 0,
                        Architecture = info.Architecture?.ToString() ?? "",
                        CurrentUsage = info.CurrentUsage,
                        L2CacheKB = info.L2CacheKB,
                        L3CacheKB = info.L3CacheKB
                    };
                }

                return new CPUInfo();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get CPU info");
                return new CPUInfo();
            }
        }

        /// <inheritdoc/>
        public async Task<MemoryInfo> GetMemoryInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11MemoryInfo");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic info = result.Output[0];
                    return new MemoryInfo
                    {
                        TotalGB = info.TotalGB ?? 0,
                        AvailableGB = info.AvailableGB ?? 0,
                        UsedGB = info.UsedGB ?? 0,
                        UsagePercent = info.UsagePercent ?? 0,
                        SlotsUsed = info.SlotsUsed ?? 0,
                        SlotsTotal = info.SlotsTotal ?? 0,
                        SpeedMHz = info.SpeedMHz,
                        Type = info.Type?.ToString()
                    };
                }

                return new MemoryInfo();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get memory info");
                return new MemoryInfo();
            }
        }

        /// <inheritdoc/>
        public async Task<List<GPUInfo>> GetGPUInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11GPUInfo");
                var gpus = new List<GPUInfo>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic gpu = item;
                        gpus.Add(new GPUInfo
                        {
                            Name = gpu.Name?.ToString() ?? "",
                            Manufacturer = gpu.Manufacturer?.ToString() ?? "",
                            DriverVersion = gpu.DriverVersion?.ToString() ?? "",
                            DriverDate = gpu.DriverDate,
                            VideoMemoryMB = gpu.VideoMemoryMB ?? 0,
                            CurrentResolution = gpu.CurrentResolution?.ToString() ?? "",
                            RefreshRate = gpu.RefreshRate,
                            Status = gpu.Status?.ToString() ?? ""
                        });
                    }
                }

                return gpus;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get GPU info");
                return new List<GPUInfo>();
            }
        }

        /// <inheritdoc/>
        public async Task<List<StorageInfo>> GetStorageInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11StorageInfo");
                var storage = new List<StorageInfo>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic disk = item;
                        storage.Add(new StorageInfo
                        {
                            Name = disk.Name?.ToString() ?? "",
                            Model = disk.Model?.ToString() ?? "",
                            MediaType = disk.MediaType?.ToString() ?? "",
                            SizeGB = disk.SizeGB ?? 0,
                            InterfaceType = disk.InterfaceType?.ToString() ?? "",
                            Status = disk.Status?.ToString() ?? "",
                            Partitions = disk.Partitions ?? 0,
                            SerialNumber = disk.SerialNumber?.ToString()
                        });
                    }
                }

                return storage;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get storage info");
                return new List<StorageInfo>();
            }
        }

        /// <inheritdoc/>
        public async Task<BIOSInfo> GetBIOSInfoAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11BIOSInfo");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic info = result.Output[0];
                    return new BIOSInfo
                    {
                        Manufacturer = info.Manufacturer?.ToString() ?? "",
                        Version = info.Version?.ToString() ?? "",
                        ReleaseDate = info.ReleaseDate,
                        SerialNumber = info.SerialNumber?.ToString(),
                        IsUEFI = info.IsUEFI ?? false,
                        SMBIOSVersion = info.SMBIOSVersion?.ToString() ?? ""
                    };
                }

                return new BIOSInfo();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get BIOS info");
                return new BIOSInfo();
            }
        }

        /// <inheritdoc/>
        public async Task<ResourceUsage> GetResourceUsageAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11ResourceUsage");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic usage = result.Output[0];
                    var resourceUsage = new ResourceUsage
                    {
                        CPUUsagePercent = usage.CPUUsagePercent ?? 0,
                        MemoryUsedGB = usage.MemoryUsedGB ?? 0,
                        MemoryTotalGB = usage.MemoryTotalGB ?? 0,
                        MemoryUsedPercent = usage.MemoryUsedPercent ?? 0,
                        Timestamp = usage.Timestamp ?? DateTime.Now
                    };

                    return resourceUsage;
                }

                return new ResourceUsage { Timestamp = DateTime.Now };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get resource usage");
                return new ResourceUsage { Timestamp = DateTime.Now };
            }
        }

        /// <inheritdoc/>
        public async Task<string> ExportSystemInfoAsync(string? path = null)
        {
            try
            {
                _logger.LogInformation("Exporting system info");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(path))
                {
                    parameters["Path"] = path;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Export-Better11SystemInfo", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic output = result.Output[0];
                    return output.Path?.ToString() ?? "";
                }

                return "";
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export system info");
                return "";
            }
        }
    }
}
