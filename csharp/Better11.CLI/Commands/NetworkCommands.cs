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
    /// Network management commands.
    /// </summary>
    public static class NetworkCommands
    {
        public static Command Build()
        {
            var command = new Command("network", "Network management commands");

            command.AddCommand(BuildListCommand());
            command.AddCommand(BuildFlushDnsCommand());
            command.AddCommand(BuildResetCommand());
            command.AddCommand(BuildDnsCommand());
            command.AddCommand(BuildTestCommand());

            return command;
        }

        private static Command BuildListCommand()
        {
            var command = new Command("list", "List network adapters");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    var adapters = await networkService.ListAdaptersAsync();

                    var table = new Table();
                    table.AddColumn("Name");
                    table.AddColumn("Status");
                    table.AddColumn("IPv4 Address");
                    table.AddColumn("MAC Address");
                    table.AddColumn("DHCP");

                    foreach (var adapter in adapters)
                    {
                        var status = adapter.Status == AdapterStatus.Up 
                            ? "[green]Up[/]" 
                            : "[red]Down[/]";
                        var dhcp = adapter.DhcpEnabled ? "Yes" : "No";

                        table.AddRow(
                            adapter.Name,
                            status,
                            adapter.IPv4Address ?? "-",
                            adapter.MacAddress ?? "-",
                            dhcp);
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

        private static Command BuildFlushDnsCommand()
        {
            var command = new Command("flush-dns", "Flush DNS resolver cache");

            command.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync("Flushing DNS cache...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await networkService.FlushDNSCacheAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]DNS cache flushed successfully![/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to flush DNS cache[/]");
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

        private static Command BuildResetCommand()
        {
            var resetCommand = new Command("reset", "Reset network components");

            // Reset TCP/IP
            var tcpipCommand = new Command("tcpip", "Reset TCP/IP stack");
            tcpipCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    AnsiConsole.MarkupLine("[yellow]Warning: This will reset the TCP/IP stack.[/]");
                    AnsiConsole.MarkupLine("[yellow]A restart may be required.[/]");
                    AnsiConsole.WriteLine();

                    if (!AnsiConsole.Confirm("Continue?"))
                    {
                        AnsiConsole.MarkupLine("[dim]Cancelled[/]");
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync("Resetting TCP/IP...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await networkService.ResetTcpIpAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]TCP/IP stack reset successfully![/]");
                                AnsiConsole.MarkupLine("[yellow]Please restart your computer to complete the reset.[/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to reset TCP/IP stack[/]");
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

            // Reset Winsock
            var winsockCommand = new Command("winsock", "Reset Winsock catalog");
            winsockCommand.SetHandler(async (InvocationContext context) =>
            {
                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    AnsiConsole.MarkupLine("[yellow]Warning: This will reset the Winsock catalog.[/]");
                    AnsiConsole.MarkupLine("[yellow]A restart may be required.[/]");
                    AnsiConsole.WriteLine();

                    if (!AnsiConsole.Confirm("Continue?"))
                    {
                        AnsiConsole.MarkupLine("[dim]Cancelled[/]");
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync("Resetting Winsock...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await networkService.ResetWinsockAsync();

                            if (success)
                            {
                                AnsiConsole.MarkupLine("[green]Winsock catalog reset successfully![/]");
                                AnsiConsole.MarkupLine("[yellow]Please restart your computer to complete the reset.[/]");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to reset Winsock catalog[/]");
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

            resetCommand.AddCommand(tcpipCommand);
            resetCommand.AddCommand(winsockCommand);

            return resetCommand;
        }

        private static Command BuildDnsCommand()
        {
            var dnsCommand = new Command("dns", "DNS configuration");

            // Set DNS
            var setCommand = new Command("set", "Set DNS servers for an adapter");
            var adapterArg = new Argument<string>("adapter", "Network adapter name");
            var providerOption = new Option<string>("--provider", "DNS provider (google, cloudflare, quad9, opendns)");
            providerOption.AddAlias("-p");
            var primaryOption = new Option<string?>("--primary", "Primary DNS server IP");
            var secondaryOption = new Option<string?>("--secondary", "Secondary DNS server IP");

            setCommand.AddArgument(adapterArg);
            setCommand.AddOption(providerOption);
            setCommand.AddOption(primaryOption);
            setCommand.AddOption(secondaryOption);

            setCommand.SetHandler(async (InvocationContext context) =>
            {
                var adapter = context.ParseResult.GetValueForArgument(adapterArg);
                var provider = context.ParseResult.GetValueForOption(providerOption);
                var primary = context.ParseResult.GetValueForOption(primaryOption);
                var secondary = context.ParseResult.GetValueForOption(secondaryOption);

                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    DNSConfiguration dnsConfig;

                    if (!string.IsNullOrEmpty(provider))
                    {
                        dnsConfig = provider.ToLowerInvariant() switch
                        {
                            "google" => DNSConfiguration.GoogleDNS,
                            "cloudflare" => DNSConfiguration.CloudflareDNS,
                            "quad9" => DNSConfiguration.Quad9DNS,
                            "opendns" => DNSConfiguration.OpenDNS,
                            _ => throw new ArgumentException($"Unknown DNS provider: {provider}")
                        };
                    }
                    else if (!string.IsNullOrEmpty(primary))
                    {
                        dnsConfig = new DNSConfiguration
                        {
                            Primary = primary,
                            Secondary = secondary
                        };
                    }
                    else
                    {
                        AnsiConsole.MarkupLine("[red]Please specify --provider or --primary[/]");
                        context.ExitCode = 1;
                        return;
                    }

                    await AnsiConsole.Status()
                        .StartAsync($"Configuring DNS for {adapter}...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await networkService.ConfigureDNSAsync(adapter, dnsConfig);

                            if (success)
                            {
                                AnsiConsole.MarkupLine($"[green]DNS configured successfully![/]");
                                AnsiConsole.MarkupLine($"  Primary: {dnsConfig.Primary}");
                                if (!string.IsNullOrEmpty(dnsConfig.Secondary))
                                {
                                    AnsiConsole.MarkupLine($"  Secondary: {dnsConfig.Secondary}");
                                }
                            }
                            else
                            {
                                AnsiConsole.MarkupLine("[red]Failed to configure DNS[/]");
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

            dnsCommand.AddCommand(setCommand);

            return dnsCommand;
        }

        private static Command BuildTestCommand()
        {
            var command = new Command("test", "Test network connectivity");
            var hostOption = new Option<string>("--host", () => "8.8.8.8", "Host to test connectivity to");
            hostOption.AddAlias("-h");
            command.AddOption(hostOption);

            command.SetHandler(async (InvocationContext context) =>
            {
                var testHost = context.ParseResult.GetValueForOption(hostOption);
                var host = context.GetHost();
                var networkService = host.Services.GetRequiredService<INetworkService>();

                try
                {
                    await AnsiConsole.Status()
                        .StartAsync($"Testing connectivity to {testHost}...", async ctx =>
                        {
                            ctx.Spinner(Spinner.Known.Dots);
                            var success = await networkService.TestConnectivityAsync(testHost!);

                            if (success)
                            {
                                AnsiConsole.MarkupLine($"[green]Connectivity test passed![/] Host {testHost} is reachable.");
                            }
                            else
                            {
                                AnsiConsole.MarkupLine($"[red]Connectivity test failed.[/] Host {testHost} is not reachable.");
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
