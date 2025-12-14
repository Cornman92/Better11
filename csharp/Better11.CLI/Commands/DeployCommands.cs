using System;
using System.Collections.Generic;
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
    /// Deployment commands including unattend generation.
    /// </summary>
    public static class DeployCommands
    {
        public static Command Build()
        {
            var command = new Command("deploy", "Deployment utilities");

            command.AddCommand(BuildUnattendCommand());

            return command;
        }

        private static Command BuildUnattendCommand()
        {
            var command = new Command("unattend", "Generate Windows unattend file");

            // Required options
            var productKeyOption = new Option<string>("--product-key", "Product key to embed in the answer file");
            productKeyOption.IsRequired = true;
            productKeyOption.AddAlias("-k");

            var outputOption = new Option<string>("--output", "Path to write unattend.xml");
            outputOption.IsRequired = true;
            outputOption.AddAlias("-o");

            // Optional options
            var languageOption = new Option<string>("--language", () => "en-US", "UI language tag");
            languageOption.AddAlias("-l");

            var timezoneOption = new Option<string>("--timezone", () => "Pacific Standard Time", "Windows time zone name");
            timezoneOption.AddAlias("-t");

            var computerNameOption = new Option<string?>("--computer-name", "Computer name to assign during setup");
            computerNameOption.AddAlias("-c");

            var adminUserOption = new Option<string>("--admin-user", () => "Administrator", "Administrative account to create");
            adminUserOption.AddAlias("-u");

            var adminPasswordOption = new Option<string?>("--admin-password", "Password for the administrative account");
            adminPasswordOption.AddAlias("-p");

            var autoLogonOption = new Option<bool>("--auto-logon", "Enable automatic logon for the admin account");
            autoLogonOption.AddAlias("-a");

            var templateOption = new Option<string?>("--template", "Start from a predefined template (workstation, lab)");

            var firstLogonOption = new Option<string[]>("--first-logon-command", "Add first-logon commands (format: 'order:command' or 'order:description|command')");
            firstLogonOption.AllowMultipleArgumentsPerToken = true;

            command.AddOption(productKeyOption);
            command.AddOption(outputOption);
            command.AddOption(languageOption);
            command.AddOption(timezoneOption);
            command.AddOption(computerNameOption);
            command.AddOption(adminUserOption);
            command.AddOption(adminPasswordOption);
            command.AddOption(autoLogonOption);
            command.AddOption(templateOption);
            command.AddOption(firstLogonOption);

            command.SetHandler(async (InvocationContext context) =>
            {
                var productKey = context.ParseResult.GetValueForOption(productKeyOption)!;
                var output = context.ParseResult.GetValueForOption(outputOption)!;
                var language = context.ParseResult.GetValueForOption(languageOption)!;
                var timezone = context.ParseResult.GetValueForOption(timezoneOption)!;
                var computerName = context.ParseResult.GetValueForOption(computerNameOption);
                var adminUser = context.ParseResult.GetValueForOption(adminUserOption)!;
                var adminPassword = context.ParseResult.GetValueForOption(adminPasswordOption);
                var autoLogon = context.ParseResult.GetValueForOption(autoLogonOption);
                var template = context.ParseResult.GetValueForOption(templateOption);
                var firstLogonCommands = context.ParseResult.GetValueForOption(firstLogonOption) ?? Array.Empty<string>();

                var host = context.GetHost();
                var unattendService = host.Services.GetRequiredService<IUnattendService>();

                try
                {
                    UnattendConfiguration config;

                    if (!string.IsNullOrEmpty(template))
                    {
                        config = template.ToLowerInvariant() switch
                        {
                            "workstation" => unattendService.CreateWorkstationTemplate(
                                productKey, adminUser, adminPassword, language, timezone),
                            "lab" => unattendService.CreateLabTemplate(productKey, language, timezone),
                            _ => throw new ArgumentException($"Unknown template: {template}")
                        };
                    }
                    else
                    {
                        config = new UnattendConfiguration
                        {
                            ProductKey = productKey,
                            Language = language,
                            InputLocale = language,
                            TimeZone = timezone,
                            ComputerName = computerName,
                            AdminPassword = adminPassword,
                            Accounts = new List<LocalAccount>
                            {
                                new LocalAccount(adminUser, adminPassword, autoLogon)
                            }
                        };
                    }

                    // Parse and add first-logon commands
                    foreach (var cmd in ParseFirstLogonCommands(firstLogonCommands))
                    {
                        config.FirstLogonCommands.Add(cmd);
                    }

                    // Validate configuration
                    var validationError = unattendService.ValidateConfiguration(config);
                    if (validationError != null)
                    {
                        AnsiConsole.MarkupLine($"[red]Validation error:[/] {validationError}");
                        context.ExitCode = 1;
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync("Generating unattend file...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var outputPath = await unattendService.GenerateUnattendAsync(config, output);
                            AnsiConsole.MarkupLine($"[green]Wrote unattend file to:[/] {outputPath}");
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

        private static List<FirstLogonCommand> ParseFirstLogonCommands(string[] rawCommands)
        {
            var commands = new List<FirstLogonCommand>();
            var index = 1;

            foreach (var raw in rawCommands)
            {
                var text = raw.Trim();
                int order = index++;
                string? description = null;
                string commandText = text;

                // Check for order prefix (e.g., "1:command")
                if (text.Contains(':'))
                {
                    var colonIndex = text.IndexOf(':');
                    var prefix = text.Substring(0, colonIndex);
                    
                    if (int.TryParse(prefix, out var parsedOrder))
                    {
                        order = parsedOrder;
                        commandText = text.Substring(colonIndex + 1).Trim();
                    }
                }

                // Check for description (e.g., "description|command")
                if (commandText.Contains('|'))
                {
                    var pipeIndex = commandText.IndexOf('|');
                    description = commandText.Substring(0, pipeIndex).Trim();
                    commandText = commandText.Substring(pipeIndex + 1).Trim();
                }

                if (!string.IsNullOrWhiteSpace(commandText))
                {
                    commands.Add(new FirstLogonCommand(order, commandText, description));
                }
            }

            return commands;
        }
    }
}
