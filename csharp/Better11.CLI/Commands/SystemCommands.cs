using System;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.CommandLine.Hosting;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    /// <summary>
    /// System optimization commands.
    /// </summary>
    public static class SystemCommands
    {
        public static Command Build()
        {
            var command = new Command("system", "System optimization commands");

            command.AddCommand(BuildStartupCommand());
            command.AddCommand(BuildDiskCommand());

            return command;
        }

        private static Command BuildStartupCommand()
        {
            var startupCommand = new Command("startup", "Startup program management");

            // List startup items
            var listCommand = new Command("list", "List startup items");
            listCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var startupService = host.Services.GetRequiredService<IStartupService>();

                try
                {
                    var items = await startupService.ListStartupItemsAsync();

                    var table = new Table();
                    table.AddColumn("Name");
                    table.AddColumn("Command");
                    table.AddColumn("Location");
                    table.AddColumn("Status");

                    foreach (var item in items)
                    {
                        var cmd = item.Command.Length > 50 
                            ? item.Command.Substring(0, 47) + "..." 
                            : item.Command;
                        var status = item.Enabled ? "[green]Enabled[/]" : "[dim]Disabled[/]";

                        table.AddRow(
                            item.Name,
                            cmd,
                            item.Location.ToString(),
                            status);
                    }

                    AnsiConsole.Write(table);
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Disable startup item
            var disableCommand = new Command("disable", "Disable a startup item");
            var nameArg = new Argument<string>("name", "Name of the startup item");
            disableCommand.AddArgument(nameArg);
            disableCommand.SetHandler(async (InvocationContext context) =>
            {
                var name = context.ParseResult.GetValueForArgument(nameArg);
                var host = context.GetHost();
                var startupService = host.Services.GetRequiredService<IStartupService>();

                try
                {
                    var success = await startupService.DisableStartupItemAsync(name);
                    
                    if (success)
                    {
                        AnsiConsole.MarkupLine($"[green]Disabled[/] startup item: {name}");
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[yellow]Could not disable[/] startup item: {name}");
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Remove startup item
            var removeCommand = new Command("remove", "Remove a startup item");
            var removeNameArg = new Argument<string>("name", "Name of the startup item");
            removeCommand.AddArgument(removeNameArg);
            removeCommand.SetHandler(async (InvocationContext context) =>
            {
                var name = context.ParseResult.GetValueForArgument(removeNameArg);
                var host = context.GetHost();
                var startupService = host.Services.GetRequiredService<IStartupService>();

                try
                {
                    var success = await startupService.RemoveStartupItemAsync(name);
                    
                    if (success)
                    {
                        AnsiConsole.MarkupLine($"[green]Removed[/] startup item: {name}");
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[yellow]Could not remove[/] startup item: {name}");
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            startupCommand.AddCommand(listCommand);
            startupCommand.AddCommand(disableCommand);
            startupCommand.AddCommand(removeCommand);

            return startupCommand;
        }

        private static Command BuildDiskCommand()
        {
            var diskCommand = new Command("disk", "Disk management commands");

            // Analyze disk space
            var analyzeCommand = new Command("analyze", "Analyze disk space");
            var driveOption = new Option<string?>("--drive", "Specific drive letter to analyze");
            driveOption.AddAlias("-d");
            analyzeCommand.AddOption(driveOption);

            analyzeCommand.SetHandler(async (InvocationContext context) =>
            {
                var drive = context.ParseResult.GetValueForOption(driveOption);
                var host = context.GetHost();
                var diskService = host.Services.GetRequiredService<IDiskService>();

                try
                {
                    if (!string.IsNullOrEmpty(drive))
                    {
                        var disk = await diskService.AnalyzeDiskSpaceAsync(drive);
                        if (disk == null)
                        {
                            AnsiConsole.MarkupLine($"[yellow]Drive {drive} not found[/]");
                            return;
                        }

                        DisplayDiskInfo(new[] { disk });
                    }
                    else
                    {
                        var disks = await diskService.AnalyzeDiskSpaceAsync();
                        DisplayDiskInfo(disks.Values);
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Cleanup temp files
            var cleanupCommand = new Command("cleanup", "Cleanup temporary files");
            var ageOption = new Option<int>("--age", () => 7, "Delete files older than this many days");
            ageOption.AddAlias("-a");
            cleanupCommand.AddOption(ageOption);

            cleanupCommand.SetHandler(async (InvocationContext context) =>
            {
                var ageDays = context.ParseResult.GetValueForOption(ageOption);
                var host = context.GetHost();
                var diskService = host.Services.GetRequiredService<IDiskService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Cleaning files older than {ageDays} days...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            
                            var result = await diskService.CleanupTempFilesAsync(ageDays);
                            
                            AnsiConsole.MarkupLine($"[green]Cleanup complete![/]");
                            AnsiConsole.MarkupLine($"  Files removed: {result.FilesRemoved}");
                            AnsiConsole.MarkupLine($"  Space freed: {result.SpaceFreedMB:F2} MB");
                            
                            if (result.LocationsCleaned.Count > 0)
                            {
                                AnsiConsole.MarkupLine($"  Locations cleaned: {string.Join(", ", result.LocationsCleaned)}");
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            diskCommand.AddCommand(analyzeCommand);
            diskCommand.AddCommand(cleanupCommand);

            return diskCommand;
        }

        private static void DisplayDiskInfo(IEnumerable<Better11.Core.Models.DiskInfo> disks)
        {
            var table = new Table();
            table.AddColumn("Drive");
            table.AddColumn("Label");
            table.AddColumn("Type");
            table.AddColumn("Total (GB)");
            table.AddColumn("Used (GB)");
            table.AddColumn("Free (GB)");
            table.AddColumn("Usage");

            foreach (var disk in disks)
            {
                var usageBar = new ProgressBar(disk.UsagePercent);
                var usageColor = disk.UsagePercent > 90 ? "red" : 
                                 disk.UsagePercent > 75 ? "yellow" : "green";
                var usageText = $"[{usageColor}]{disk.UsagePercent:F1}%[/]";

                table.AddRow(
                    disk.DriveLetter,
                    disk.Label ?? "-",
                    disk.DriveType.ToString(),
                    $"{disk.TotalGB:F2}",
                    $"{disk.UsedGB:F2}",
                    $"{disk.FreeGB:F2}",
                    usageText);
            }

            AnsiConsole.Write(table);
        }

        private class ProgressBar
        {
            private readonly double _percent;
            public ProgressBar(double percent) => _percent = percent;
        }
    }
}
