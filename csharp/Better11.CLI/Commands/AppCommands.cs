using System;
using System.CommandLine;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    public class AppCommands
    {
        private readonly IServiceProvider _services;

        public AppCommands(IServiceProvider services)
        {
            _services = services;
        }

        public Command CreateCommand()
        {
            var appCommand = new Command("app", "Application management commands");

            // list command
            var listCommand = new Command("list", "List available applications");
            listCommand.SetHandler(async () => await ListAppsAsync());
            appCommand.AddCommand(listCommand);

            // install command
            var installCommand = new Command("install", "Install an application");
            var appIdArg = new Argument<string>("app-id", "Application ID to install");
            var forceOption = new Option<bool>("--force", "Skip confirmation prompts");
            installCommand.AddArgument(appIdArg);
            installCommand.AddOption(forceOption);
            installCommand.SetHandler(async (appId, force) => await InstallAppAsync(appId, force), appIdArg, forceOption);
            appCommand.AddCommand(installCommand);

            // uninstall command
            var uninstallCommand = new Command("uninstall", "Uninstall an application");
            uninstallCommand.AddArgument(appIdArg);
            uninstallCommand.AddOption(forceOption);
            uninstallCommand.SetHandler(async (appId, force) => await UninstallAppAsync(appId, force), appIdArg, forceOption);
            appCommand.AddCommand(uninstallCommand);

            // status command
            var statusCommand = new Command("status", "Show application status");
            var statusAppIdArg = new Argument<string?>("app-id", () => null, "Application ID (optional)");
            statusCommand.AddArgument(statusAppIdArg);
            statusCommand.SetHandler(async (appId) => await ShowStatusAsync(appId), statusAppIdArg);
            appCommand.AddCommand(statusCommand);

            return appCommand;
        }

        private async Task ListAppsAsync()
        {
            var appManager = _services.GetRequiredService<IAppManagerService>();

            try
            {
                AnsiConsole.Status()
                    .Start("Loading applications...", ctx =>
                    {
                        var apps = appManager.ListAvailableAppsAsync().Result;

                        var table = new Table();
                        table.AddColumn("App ID");
                        table.AddColumn("Name");
                        table.AddColumn("Version");
                        table.AddColumn("Type");
                        table.AddColumn("Status");

                        foreach (var app in apps)
                        {
                            table.AddRow(
                                app.AppId,
                                app.Name,
                                app.Version,
                                app.InstallerType.ToString(),
                                app.IsInstalled ? "[green]Installed[/]" : "[yellow]Available[/]"
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

        private async Task InstallAppAsync(string appId, bool force)
        {
            var appManager = _services.GetRequiredService<IAppManagerService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync($"Installing {appId}...", async ctx =>
                    {
                        var result = await appManager.InstallAppAsync(appId, force);

                        if (result.Success)
                        {
                            AnsiConsole.MarkupLine($"[green]✓[/] Successfully installed {appId} v{result.Version}");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine($"[red]✗[/] Installation failed: {result.ErrorMessage}");
                        }
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task UninstallAppAsync(string appId, bool force)
        {
            var appManager = _services.GetRequiredService<IAppManagerService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync($"Uninstalling {appId}...", async ctx =>
                    {
                        var result = await appManager.UninstallAppAsync(appId, force);

                        if (result.Success)
                        {
                            AnsiConsole.MarkupLine($"[green]✓[/] Successfully uninstalled {appId}");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine($"[red]✗[/] Uninstall failed: {result.ErrorMessage}");
                        }
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task ShowStatusAsync(string? appId)
        {
            var appManager = _services.GetRequiredService<IAppManagerService>();

            try
            {
                if (appId != null)
                {
                    var status = await appManager.GetAppStatusAsync(appId);
                    if (status != null)
                    {
                        var panel = new Panel(
                            $"App ID: {status.AppId}\n" +
                            $"Version: {status.Version}\n" +
                            $"Installed: {(status.Installed ? "Yes" : "No")}\n" +
                            $"Installer Path: {status.InstallerPath}"
                        );
                        panel.Header = new PanelHeader($"Status: {appId}");
                        AnsiConsole.Write(panel);
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[yellow]Application {appId} not found[/]");
                    }
                }
                else
                {
                    var apps = await appManager.ListInstalledAppsAsync();
                    var table = new Table();
                    table.AddColumn("App ID");
                    table.AddColumn("Version");

                    foreach (var app in apps)
                    {
                        table.AddRow(app.AppId, app.Version);
                    }

                    AnsiConsole.Write(table);
                }
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }
    }
}
