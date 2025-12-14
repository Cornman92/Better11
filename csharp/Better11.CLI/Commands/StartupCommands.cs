using System;
using System.CommandLine;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    public class StartupCommands
    {
        private readonly IServiceProvider _services;

        public StartupCommands(IServiceProvider services)
        {
            _services = services;
        }

        public Command CreateCommand()
        {
            var startupCommand = new Command("startup", "Startup programs management");

            // list command
            var listCommand = new Command("list", "List startup programs");
            listCommand.SetHandler(async () => await ListStartupItemsAsync());
            startupCommand.AddCommand(listCommand);

            // disable command
            var disableCommand = new Command("disable", "Disable a startup program");
            var nameArg = new Argument<string>("name", "Program name");
            disableCommand.AddArgument(nameArg);
            disableCommand.SetHandler(async (name) => await DisableStartupItemAsync(name), nameArg);
            startupCommand.AddCommand(disableCommand);

            // enable command
            var enableCommand = new Command("enable", "Enable a startup program");
            enableCommand.AddArgument(nameArg);
            enableCommand.SetHandler(async (name) => await EnableStartupItemAsync(name), nameArg);
            startupCommand.AddCommand(enableCommand);

            return startupCommand;
        }

        private async Task ListStartupItemsAsync()
        {
            var startupService = _services.GetRequiredService<IStartupService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync("Loading startup items...", async ctx =>
                    {
                        var items = await startupService.ListStartupItemsAsync();

                        var table = new Table();
                        table.AddColumn("Name");
                        table.AddColumn("Command");
                        table.AddColumn("Location");
                        table.AddColumn("Status");

                        foreach (var item in items)
                        {
                            var command = item.Command.Length > 50 ? item.Command.Substring(0, 47) + "..." : item.Command;
                            table.AddRow(
                                item.Name,
                                command,
                                item.Location.ToString(),
                                item.Enabled ? "[green]Enabled[/]" : "[yellow]Disabled[/]"
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

        private async Task DisableStartupItemAsync(string name)
        {
            var startupService = _services.GetRequiredService<IStartupService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync($"Disabling {name}...", async ctx =>
                    {
                        var success = await startupService.DisableStartupItemAsync(name, Better11.Core.Models.StartupLocation.Registry);

                        if (success)
                        {
                            AnsiConsole.MarkupLine($"[green]✓[/] Disabled {name}");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine($"[red]✗[/] Failed to disable {name}");
                        }
                    });
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task EnableStartupItemAsync(string name)
        {
            var startupService = _services.GetRequiredService<IStartupService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync($"Enabling {name}...", async ctx =>
                    {
                        var success = await startupService.EnableStartupItemAsync(name, Better11.Core.Models.StartupLocation.Registry);

                        if (success)
                        {
                            AnsiConsole.MarkupLine($"[green]✓[/] Enabled {name}");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine($"[red]✗[/] Failed to enable {name}");
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
