using System;
using System.CommandLine;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    public class PrivacyCommands
    {
        private readonly IServiceProvider _services;

        public PrivacyCommands(IServiceProvider services)
        {
            _services = services;
        }

        public Command CreateCommand()
        {
            var privacyCommand = new Command("privacy", "Privacy settings commands");

            // telemetry command
            var telemetryCommand = new Command("telemetry", "Manage telemetry settings");
            
            var getCommand = new Command("get", "Get current telemetry level");
            getCommand.SetHandler(async () => await GetTelemetryLevelAsync());
            telemetryCommand.AddCommand(getCommand);

            var setCommand = new Command("set", "Set telemetry level");
            var levelArg = new Argument<string>("level", "Telemetry level (Security, Basic, Enhanced, Full)");
            setCommand.AddArgument(levelArg);
            setCommand.SetHandler(async (level) => await SetTelemetryLevelAsync(level), levelArg);
            telemetryCommand.AddCommand(setCommand);

            privacyCommand.AddCommand(telemetryCommand);

            // cortana command
            var cortanaCommand = new Command("cortana", "Manage Cortana");
            var disableCommand = new Command("disable", "Disable Cortana");
            disableCommand.SetHandler(async () => await DisableCortanaAsync());
            cortanaCommand.AddCommand(disableCommand);
            privacyCommand.AddCommand(cortanaCommand);

            return privacyCommand;
        }

        private async Task GetTelemetryLevelAsync()
        {
            var privacyService = _services.GetRequiredService<IPrivacyService>();

            try
            {
                var level = await privacyService.GetTelemetryLevelAsync();
                AnsiConsole.MarkupLine($"Current telemetry level: [cyan]{level}[/]");
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task SetTelemetryLevelAsync(string levelStr)
        {
            var privacyService = _services.GetRequiredService<IPrivacyService>();

            try
            {
                if (Enum.TryParse<TelemetryLevel>(levelStr, true, out var level))
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Setting telemetry level to {level}...", async ctx =>
                        {
                            var success = await privacyService.SetTelemetryLevelAsync(level, true);

                            if (success)
                            {
                                AnsiConsole.MarkupLine($"[green]✓[/] Telemetry level set to {level}");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]✗[/] Failed to set telemetry level");
                            }
                        });
                }
                else
                {
                    AnsiConsole.MarkupLine($"[red]Invalid telemetry level:[/] {levelStr}");
                    AnsiConsole.MarkupLine("Valid levels: Security, Basic, Enhanced, Full");
                }
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
            }
        }

        private async Task DisableCortanaAsync()
        {
            var privacyService = _services.GetRequiredService<IPrivacyService>();

            try
            {
                await AnsiConsole.Status()
                    .StartAsync("Disabling Cortana...", async ctx =>
                    {
                        var success = await privacyService.DisableCortanaAsync(true);

                        if (success)
                        {
                            AnsiConsole.MarkupLine("[green]✓[/] Cortana disabled");
                        }
                        else
                        {
                            AnsiConsole.MarkupLine("[red]✗[/] Failed to disable Cortana");
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
