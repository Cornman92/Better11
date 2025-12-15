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
    /// Power management commands.
    /// </summary>
    public static class PowerCommands
    {
        public static Command Build()
        {
            var command = new Command("power", "Power management commands");

            command.AddCommand(BuildListCommand());
            command.AddCommand(BuildSetCommand());
            command.AddCommand(BuildHibernateCommand());
            command.AddCommand(BuildBatteryCommand());

            return command;
        }

        private static Command BuildListCommand()
        {
            var command = new Command("list", "List power plans");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var powerService = host.Services.GetRequiredService<IPowerService>();

                try
                {
                    var plans = await powerService.ListPowerPlansAsync();

                    var table = new Table();
                    table.AddColumn("Name");
                    table.AddColumn("Type");
                    table.AddColumn("Status");
                    table.AddColumn("GUID");

                    foreach (var plan in plans)
                    {
                        var status = plan.IsActive ? "[green]Active[/]" : "[dim]Inactive[/]";

                        table.AddRow(
                            plan.Name,
                            plan.Type.ToString(),
                            status,
                            plan.Guid);
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

        private static Command BuildSetCommand()
        {
            var command = new Command("set", "Set active power plan");
            var nameArg = new Argument<string>("name", "Power plan name or GUID");
            command.AddArgument(nameArg);

            command.SetHandler(async (InvocationContext context) =>
            {
                var name = context.ParseResult.GetValueForArgument(nameArg);
                var host = context.GetHost();
                var powerService = host.Services.GetRequiredService<IPowerService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Setting power plan to {name}...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            
                            bool success;
                            // Check if it looks like a GUID
                            if (Guid.TryParse(name, out _))
                            {
                                success = await powerService.SetActivePlanAsync(name);
                            }
                            else
                            {
                                success = await powerService.SetActivePlanByNameAsync(name);
                            }

                            if (success)
                            {
                                AnsiConsole.MarkupLine($"[green]Power plan set to:[/] {name}");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine($"[red]Failed to set power plan[/]");
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

        private static Command BuildHibernateCommand()
        {
            var hibernateCommand = new Command("hibernate", "Manage hibernation settings");

            // Enable hibernation
            var enableCommand = new Command("enable", "Enable hibernation");
            enableCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var powerService = host.Services.GetRequiredService<IPowerService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Enabling hibernation...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await powerService.EnableHibernationAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]Hibernation enabled[/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to enable hibernation[/]");
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

            // Disable hibernation
            var disableCommand = new Command("disable", "Disable hibernation");
            disableCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var powerService = host.Services.GetRequiredService<IPowerService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Disabling hibernation...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await powerService.DisableHibernationAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]Hibernation disabled[/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to disable hibernation[/]");
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

            hibernateCommand.AddCommand(enableCommand);
            hibernateCommand.AddCommand(disableCommand);

            return hibernateCommand;
        }

        private static Command BuildBatteryCommand()
        {
            var command = new Command("battery-report", "Generate battery health report");
            var outputOption = new Option<string?>("--output", "Output path for the report");
            outputOption.AddAlias("-o");
            command.AddOption(outputOption);

            command.SetHandler(async (InvocationContext context) =>
            {
                var output = context.ParseResult.GetValueForOption(outputOption);
                var host = context.GetHost();
                var powerService = host.Services.GetRequiredService<IPowerService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Generating battery report...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var reportPath = await powerService.GenerateBatteryReportAsync(output);

                            if (reportPath != null)
                            {
                                AnsiConsole.MarkupLine($"[green]Battery report generated:[/] {reportPath}");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to generate battery report[/]");
                                AnsiConsole.MarkupLine("[dim]Note: This feature requires a laptop with a battery[/]");
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
