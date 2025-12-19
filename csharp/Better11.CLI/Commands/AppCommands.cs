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
    /// Application management commands.
    /// </summary>
    public static class AppCommands
    {
        public static Command Build()
        {
            var command = new Command("apps", "Application management commands");

            command.AddCommand(BuildListCommand());
            command.AddCommand(BuildDownloadCommand());
            command.AddCommand(BuildInstallCommand());
            command.AddCommand(BuildUninstallCommand());
            command.AddCommand(BuildStatusCommand());
            command.AddCommand(BuildPlanCommand());

            return command;
        }

        private static Command BuildListCommand()
        {
            var command = new Command("list", "List available applications");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    var apps = await appService.ListAvailableAsync();

                    var table = new Table();
                    table.AddColumn("App ID");
                    table.AddColumn("Name");
                    table.AddColumn("Version");
                    table.AddColumn("Type");

                    foreach (var app in apps)
                    {
                        table.AddRow(
                            app.AppId,
                            app.Name,
                            app.Version,
                            app.InstallerType.ToString().ToLower());
                    }

                    AnsiConsole.Write(table);
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildDownloadCommand()
        {
            var appIdArg = new Argument<string>("app-id", "Application ID to download");
            var command = new Command("download", "Download an application");
            command.AddArgument(appIdArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var appId = context.ParseResult.GetValueForArgument(appIdArg);
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    AnsiConsole.MarkupLine($"[blue]Downloading[/] {appId}...");
                    
                    var path = await appService.DownloadAsync(appId);
                    
                    AnsiConsole.MarkupLine($"[green]Downloaded to:[/] {path}");
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Download failed:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildInstallCommand()
        {
            var appIdArg = new Argument<string>("app-id", "Application ID to install");
            var command = new Command("install", "Download, verify, and install an application");
            command.AddArgument(appIdArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var appId = context.ParseResult.GetValueForArgument(appIdArg);
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Installing {appId}...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            
                            var (status, result) = await appService.InstallAsync(appId);
                            
                            if (result.Success)
                            {
                                AnsiConsole.MarkupLine($"[green]Installed[/] {status.AppId} v{status.Version}");
                                if (result.Command.Count > 0)
                                {
                                    AnsiConsole.MarkupLine($"[dim]Command: {string.Join(" ", result.Command)}[/]");
                                }
                            }
                            else
                            {
                                AnsiConsole.MarkupLine($"[yellow]Installation completed with warnings[/]");
                                if (!string.IsNullOrEmpty(result.StandardError))
                                {
                                    AnsiConsole.MarkupLine($"[red]{result.StandardError}[/]");
                                }
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Installation failed:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildUninstallCommand()
        {
            var appIdArg = new Argument<string>("app-id", "Application ID to uninstall");
            var command = new Command("uninstall", "Uninstall an installed application");
            command.AddArgument(appIdArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var appId = context.ParseResult.GetValueForArgument(appIdArg);
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Uninstalling {appId}...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            
                            var result = await appService.UninstallAsync(appId);
                            
                            if (result.Success)
                            {
                                AnsiConsole.MarkupLine($"[green]Uninstalled[/] {appId}");
                                AnsiConsole.MarkupLine($"[dim]Command: {string.Join(" ", result.Command)}[/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine($"[red]Uninstall failed[/]");
                                if (!string.IsNullOrEmpty(result.StandardError))
                                {
                                    AnsiConsole.MarkupLine($"[red]{result.StandardError}[/]");
                                }
                            }
                        });
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Uninstall failed:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildStatusCommand()
        {
            var appIdArg = new Argument<string?>("app-id", () => null, "Optional application ID");
            var command = new Command("status", "Show installation status");
            command.AddArgument(appIdArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var appId = context.ParseResult.GetValueForArgument(appIdArg);
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    var statuses = await appService.GetStatusAsync(appId);

                    if (statuses.Count == 0)
                    {
                        AnsiConsole.MarkupLine("[dim]No status recorded[/]");
                        return;
                    }

                    var table = new Table();
                    table.AddColumn("App ID");
                    table.AddColumn("Version");
                    table.AddColumn("Status");
                    table.AddColumn("Install Date");

                    foreach (var status in statuses)
                    {
                        var statusText = status.Installed ? "[green]Installed[/]" : "[dim]Not installed[/]";
                        var dateText = status.InstallDate?.ToString("yyyy-MM-dd HH:mm") ?? "-";
                        
                        table.AddRow(
                            status.AppId,
                            status.Version,
                            statusText,
                            dateText);
                    }

                    AnsiConsole.Write(table);
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }

        private static Command BuildPlanCommand()
        {
            var appIdArg = new Argument<string>("app-id", "Application ID to plan for");
            var command = new Command("plan", "Show the installation plan for an application");
            command.AddArgument(appIdArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var appId = context.ParseResult.GetValueForArgument(appIdArg);
                var host = context.GetHost();
                var appService = host.Services.GetRequiredService<IAppService>();

                try
                {
                    var plan = await appService.GetInstallPlanAsync(appId);

                    if (plan.Steps.Count == 0)
                    {
                        AnsiConsole.MarkupLine("[dim]No plan steps found[/]");
                        return;
                    }

                    // Display table
                    var table = new Table();
                    table.AddColumn("Action");
                    table.AddColumn("App ID");
                    table.AddColumn("Version");
                    table.AddColumn("Status");
                    table.AddColumn("Notes");

                    foreach (var step in plan.Steps)
                    {
                        var actionColor = step.Action switch
                        {
                            "install" => "blue",
                            "skip" => "green",
                            "blocked" => "red",
                            _ => "white"
                        };
                        var actionText = $"[{actionColor}]{step.Action.ToUpper()}[/]";
                        var statusText = step.Installed ? "[green]installed[/]" : "[dim]pending[/]";
                        var notes = string.IsNullOrEmpty(step.Notes) ? "-" : $"[yellow]{step.Notes}[/]";

                        table.AddRow(
                            actionText,
                            step.AppId,
                            step.Version,
                            statusText,
                            notes);
                    }

                    AnsiConsole.Write(table);

                    // Display warnings
                    if (plan.Warnings.Count > 0)
                    {
                        AnsiConsole.WriteLine();
                        AnsiConsole.MarkupLine("[yellow]Warnings:[/]");
                        foreach (var warning in plan.Warnings)
                        {
                            AnsiConsole.MarkupLine($"  [yellow]-[/] {warning}");
                        }
                    }

                    // Display summary
                    AnsiConsole.WriteLine();
                    var installCount = plan.InstallCount();
                    var skipCount = plan.SkipCount();
                    var hasBlocked = plan.HasBlockedSteps();

                    if (hasBlocked)
                    {
                        AnsiConsole.MarkupLine("[red]Installation cannot proceed due to blocked dependencies[/]");
                        context.ExitCode = 1;
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[dim]Plan: {installCount} to install, {skipCount} to skip[/]");
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Planning failed:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            return command;
        }
    }
}
