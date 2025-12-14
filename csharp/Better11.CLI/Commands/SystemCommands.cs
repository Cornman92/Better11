using System;
using System.CommandLine;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    public class SystemCommands
    {
        private readonly IServiceProvider _services;

        public SystemCommands(IServiceProvider services)
        {
            _services = services;
        }

        public Command CreateCommand()
        {
            var systemCommand = new Command("system", "System tools commands");

            // disk command
            var diskCommand = new Command("disk", "Disk management");
            diskCommand.SetHandler(async () => await ShowDiskInfoAsync());
            systemCommand.AddCommand(diskCommand);

            // cleanup command
            var cleanupCommand = new Command("cleanup", "Cleanup temporary files");
            var daysOption = new Option<int>("--days", () => 7, "Age of files to remove (days)");
            cleanupCommand.AddOption(daysOption);
            cleanupCommand.SetHandler(async (days) => await CleanupTempFilesAsync(days), daysOption);
            systemCommand.AddCommand(cleanupCommand);

            // restore-point command
            var restoreCommand = new Command("restore-point", "Create system restore point");
            var descArg = new Argument<string>("description", "Restore point description");
            restoreCommand.AddArgument(descArg);
            restoreCommand.SetHandler(async (desc) => await CreateRestorePointAsync(desc), descArg);
            systemCommand.AddCommand(restoreCommand);

            return systemCommand;
        }

        private async Task ShowDiskInfoAsync()
        {
            var diskService = _services.GetRequiredService<IDiskService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync("Analyzing disk space...", async ctx =>
                    {
                        var disks = await diskService.AnalyzeDiskSpaceAsync();

                        var table = new Table();
                        table.AddColumn("Drive");
                        table.AddColumn("Label");
                        table.AddColumn("Total (GB)");
                        table.AddColumn("Used (GB)");
                        table.AddColumn("Free (GB)");
                        table.AddColumn("Usage %");

                        foreach (var disk in disks.Values)
                        {
                            var usagePercent = (double)disk.UsedBytes / disk.TotalBytes * 100;
                            var usageColor = usagePercent > 90 ? "red" : usagePercent > 75 ? "yellow" : "green";

                            table.AddRow(
                                disk.DriveLetter,
                                disk.Label,
                                $"{disk.TotalBytes / (1024.0 * 1024 * 1024):F2}",
                                $"{disk.UsedBytes / (1024.0 * 1024 * 1024):F2}",
                                $"{disk.FreeBytes / (1024.0 * 1024 * 1024):F2}",
                                $"[{usageColor}]{usagePercent:F1}%[/]"
                            );
                        }

                        AnsiConsole.Write(table);
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task CleanupTempFilesAsync(int days)
        {
            var diskService = _services.GetRequiredService<IDiskService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync($"Cleaning temporary files older than {days} days...", async ctx =>
                    {
                        var result = await diskService.CleanupTempFilesAsync(days);

                        AnsiConsole.MarkupLine($"[green]✓[/] Cleaned {result.FilesRemoved} files");
                        AnsiConsole.MarkupLine($"[green]✓[/] Freed {result.SpaceFreedBytes / (1024.0 * 1024):F2} MB");
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task CreateRestorePointAsync(string description)
        {
            var systemTools = _services.GetRequiredService<ISystemToolsService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync("Creating restore point...", async ctx =>
                    {
                        var success = await systemTools.CreateRestorePointAsync(description);

                        if (success)
                        {
                            AnsiConsole.MarkupLine($"[green]✓[/] Restore point created: {description}");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine("[red]✗[/] Failed to create restore point");
                        }
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }
    }
}
