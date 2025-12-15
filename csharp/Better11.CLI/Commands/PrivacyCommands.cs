using System;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.CommandLine.Hosting;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Spectre.Console;

namespace Better11.CLI.Commands
{
    /// <summary>
    /// Privacy and telemetry commands.
    /// </summary>
    public static class PrivacyCommands
    {
        public static Command Build()
        {
            var command = new Command("privacy", "Privacy and telemetry settings");

            command.AddCommand(BuildStatusCommand());
            command.AddCommand(BuildTelemetryCommand());
            command.AddCommand(BuildCortanaCommand());
            command.AddCommand(BuildRecommendedCommand());

            return command;
        }

        private static Command BuildStatusCommand()
        {
            var command = new Command("status", "Show current privacy settings");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    var status = await privacyService.GetPrivacyStatusAsync();

                    var table = new Table();
                    table.AddColumn("Setting");
                    table.AddColumn("Status");

                    table.AddRow("Telemetry Level", FormatTelemetryLevel(status.TelemetryLevel));
                    table.AddRow("Cortana", FormatEnabled(status.CortanaEnabled));
                    table.AddRow("Location Services", FormatEnabled(status.LocationEnabled));
                    table.AddRow("Advertising ID", FormatEnabled(status.AdvertisingIdEnabled));
                    table.AddRow("Activity History", FormatEnabled(status.ActivityHistoryEnabled));

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

        private static Command BuildTelemetryCommand()
        {
            var command = new Command("telemetry", "Manage telemetry settings");

            // Get telemetry level
            var getCommand = new Command("get", "Get current telemetry level");
            getCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    var level = await privacyService.GetTelemetryLevelAsync();
                    AnsiConsole.MarkupLine($"Current telemetry level: {FormatTelemetryLevel(level)}");
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Set telemetry level
            var setCommand = new Command("set", "Set telemetry level");
            var levelArg = new Argument<string>("level", "Telemetry level (security, basic, enhanced, full)");
            setCommand.AddArgument(levelArg);

            setCommand.SetHandler(async (InvocationContext context) =>
            {
                var levelStr = context.ParseResult.GetValueForArgument(levelArg);
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    var level = levelStr.ToLowerInvariant() switch
                    {
                        "security" => TelemetryLevel.Security,
                        "basic" => TelemetryLevel.Basic,
                        "enhanced" => TelemetryLevel.Enhanced,
                        "full" => TelemetryLevel.Full,
                        _ => throw new ArgumentException($"Invalid telemetry level: {levelStr}")
                    };

                    var success = await privacyService.SetTelemetryLevelAsync(level);

                    if (success)
                    {
                        AnsiConsole.MarkupLine($"[green]Telemetry level set to:[/] {FormatTelemetryLevel(level)}");
                    }
                    else
                    {
                        AnsiConsole.MarkupLine($"[red]Failed to set telemetry level[/]");
                        context.ExitCode = 1;
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            command.AddCommand(getCommand);
            command.AddCommand(setCommand);

            return command;
        }

        private static Command BuildCortanaCommand()
        {
            var command = new Command("cortana", "Manage Cortana settings");

            // Enable Cortana
            var enableCommand = new Command("enable", "Enable Cortana");
            enableCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    var success = await privacyService.SetCortanaEnabledAsync(true);

                    if (success)
                    {
                        AnsiConsole.MarkupLine("[green]Cortana enabled[/]");
                    }
                    else
                    {
                        AnsiConsole.MarkupLine("[red]Failed to enable Cortana[/]");
                        context.ExitCode = 1;
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            // Disable Cortana
            var disableCommand = new Command("disable", "Disable Cortana");
            disableCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    var success = await privacyService.SetCortanaEnabledAsync(false);

                    if (success)
                    {
                        AnsiConsole.MarkupLine("[green]Cortana disabled[/]");
                    }
                    else
                    {
                        AnsiConsole.MarkupLine("[red]Failed to disable Cortana[/]");
                        context.ExitCode = 1;
                    }
                }
                catch (Exception ex)
                {
                    AnsiConsole.MarkupLine($"[red]Error:[/] {ex.Message}");
                    context.ExitCode = 1;
                }
            });

            command.AddCommand(enableCommand);
            command.AddCommand(disableCommand);

            return command;
        }

        private static Command BuildRecommendedCommand()
        {
            var command = new Command("apply-recommended", "Apply recommended privacy settings");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var privacyService = host.Services.GetRequiredService<IPrivacyService>();

                try
                {
                    AnsiConsole.MarkupLine("[blue]Applying recommended privacy settings...[/]");
                    AnsiConsole.MarkupLine("This will:");
                    AnsiConsole.MarkupLine("  - Set telemetry to Basic");
                    AnsiConsole.MarkupLine("  - Disable Cortana");
                    AnsiConsole.MarkupLine("  - Disable Advertising ID");
                    AnsiConsole.MarkupLine("  - Disable Activity History");
                    AnsiConsole.WriteLine();

                    if (!AnsiConsole.Confirm("Continue?"))
                    {
                        AnsiConsole.MarkupLine("[dim]Cancelled[/]");
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync("Applying settings...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await privacyService.ApplyRecommendedSettingsAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]Recommended privacy settings applied successfully![/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[yellow]Some settings may not have been applied[/]");
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

        private static string FormatTelemetryLevel(TelemetryLevel level)
        {
            return level switch
            {
                TelemetryLevel.Security => "[green]Security (Minimum)[/]",
                TelemetryLevel.Basic => "[blue]Basic[/]",
                TelemetryLevel.Enhanced => "[yellow]Enhanced[/]",
                TelemetryLevel.Full => "[red]Full[/]",
                _ => "[dim]Unknown[/]"
            };
        }

        private static string FormatEnabled(bool enabled)
        {
            return enabled ? "[red]Enabled[/]" : "[green]Disabled[/]";
        }
    }
}
