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
    /// Backup and restore commands.
    /// </summary>
    public static class BackupCommands
    {
        public static Command Build()
        {
            var command = new Command("backup", "Backup and restore commands");

            command.AddCommand(BuildRestorePointsCommand());
            command.AddCommand(BuildExportCommand());
            command.AddCommand(BuildImportCommand());

            return command;
        }

        private static Command BuildRestorePointsCommand()
        {
            var restoreCommand = new Command("restore-points", "System restore point management");

            // List restore points
            var listCommand = new Command("list", "List available restore points");
            listCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var backupService = host.Services.GetRequiredService<IBackupService>();

                try
                {
                    var points = await backupService.ListRestorePointsAsync();

                    if (points.Count == 0)
                    {
                        AnsiConsole.MarkupLine("[dim]No restore points found[/]");
                        return;
                    }

                    var table = new Table();
                    table.AddColumn("#");
                    table.AddColumn("Description");
                    table.AddColumn("Date");
                    table.AddColumn("Type");

                    foreach (var point in points)
                    {
                        table.AddRow(
                            point.SequenceNumber.ToString(),
                            point.Description,
                            point.CreationTime.ToString("yyyy-MM-dd HH:mm"),
                            point.RestorePointType);
                    }

                    AnsiConsole.Write(table);
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Create restore point
            var createCommand = new Command("create", "Create a new restore point");
            var descriptionArg = new Argument<string>("description", "Description for the restore point");
            createCommand.AddArgument(descriptionArg);

            createCommand.SetHandler(async (InvocationContext context) =>
            {
                var description = context.ParseResult.GetValueForArgument(descriptionArg);
                var host = context.GetHost();
                var backupService = host.Services.GetRequiredService<IBackupService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Creating restore point...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var point = await backupService.CreateRestorePointAsync(description);

                            if (point != null)
                            {
                                AnsiConsole.MarkupLine($"[green]Restore point created![/]");
                                AnsiConsole.MarkupLine($"  Sequence: {point.SequenceNumber}");
                                AnsiConsole.MarkupLine($"  Description: {point.Description}");
                                AnsiConsole.MarkupLine($"  Created: {point.CreationTime:yyyy-MM-dd HH:mm}");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to create restore point[/]");
                                AnsiConsole.MarkupLine("[dim]Note: Administrator privileges may be required[/]");
                                context.ExitCode = 1;
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            restoreCommand.AddCommand(listCommand);
            restoreCommand.AddCommand(createCommand);

            return restoreCommand;
        }

        private static Command BuildExportCommand()
        {
            var command = new Command("export", "Export Better11 settings");
            var outputArg = new Argument<string>("output", "Output file path");
            command.AddArgument(outputArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var output = context.ParseResult.GetValueForArgument(outputArg);
                var host = context.GetHost();
                var backupService = host.Services.GetRequiredService<IBackupService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Exporting settings...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var result = await backupService.ExportSettingsAsync(output);

                            if (result.Success)
                            {
                                AnsiConsole.MarkupLine($"[green]Settings exported successfully![/]");
                                AnsiConsole.MarkupLine($"  Path: {result.BackupPath}");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine($"[red]Failed to export settings:[/] {result.Message}");
                                context.ExitCode = 1;
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildImportCommand()
        {
            var command = new Command("import", "Import Better11 settings");
            var inputArg = new Argument<string>("input", "Input file path");
            command.AddArgument(inputArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var input = context.ParseResult.GetValueForArgument(inputArg);
                var host = context.GetHost();
                var backupService = host.Services.GetRequiredService<IBackupService>();

                try
                {
                    AnsiConsole.MarkupLine("[yellow]Warning: This will overwrite current settings.[/]");
                    AnsiConsole.WriteLine();

                    if (!AnsiConsole.Confirm("Continue?"))
                    {
                        AnsiConsole.MarkupLine("[dim]Cancelled[/]");
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync("Importing settings...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await backupService.ImportSettingsAsync(input);

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]Settings imported successfully![/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to import settings[/]");
                                context.ExitCode = 1;
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }
    }
}
