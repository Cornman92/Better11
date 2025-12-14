using System;
using System.CommandLine;
using System.CommandLine.Builder;
using System.CommandLine.Hosting;
using System.CommandLine.Parsing;
using System.IO;
using System.Threading.Tasks;
using Better11.CLI.Commands;
using Better11.Core.Interfaces;
using Better11.Core.PowerShell;
using Better11.Core.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace Better11.CLI
{
    /// <summary>
    /// Better11 CLI application entry point.
    /// </summary>
    public class Program
    {
        public static async Task<int> Main(string[] args)
        {
            var rootCommand = BuildRootCommand();

            var parser = new CommandLineBuilder(rootCommand)
                .UseDefaults()
                .UseHost(_ => Host.CreateDefaultBuilder(args), builder =>
                {
                    builder.ConfigureServices((context, services) =>
                    {
                        ConfigureServices(services);
                    });
                    builder.ConfigureLogging(logging =>
                    {
                        logging.SetMinimumLevel(LogLevel.Warning);
                    });
                })
                .Build();

            return await parser.InvokeAsync(args);
        }

        private static RootCommand BuildRootCommand()
        {
            var rootCommand = new RootCommand("Better11 - Windows Enhancement Toolkit CLI")
            {
                Name = "better11"
            };

            // Global options
            var catalogOption = new Option<string>(
                "--catalog",
                getDefaultValue: () => GetDefaultCatalogPath(),
                description: "Path to the app catalog JSON file");
            rootCommand.AddGlobalOption(catalogOption);

            var verboseOption = new Option<bool>(
                "--verbose",
                description: "Enable verbose output");
            verboseOption.AddAlias("-v");
            rootCommand.AddGlobalOption(verboseOption);

            // Add subcommands
            rootCommand.AddCommand(AppCommands.Build());
            rootCommand.AddCommand(SystemCommands.Build());
            rootCommand.AddCommand(PrivacyCommands.Build());
            rootCommand.AddCommand(NetworkCommands.Build());
            rootCommand.AddCommand(PowerCommands.Build());
            rootCommand.AddCommand(BackupCommands.Build());
            rootCommand.AddCommand(DeployCommands.Build());

            return rootCommand;
        }

        private static void ConfigureServices(IServiceCollection services)
        {
            // Register PowerShell executor
            services.AddSingleton<PowerShellExecutor>();

            // Register services
            services.AddSingleton<IDiskService, DiskService>();
            services.AddSingleton<IPowerService, PowerService>();
            services.AddSingleton<INetworkService, NetworkService>();
            services.AddSingleton<IStartupService, StartupService>();
            services.AddSingleton<IPrivacyService, PrivacyService>();
            services.AddSingleton<IBackupService, BackupService>();
            services.AddSingleton<IUnattendService, UnattendService>();

            // Register app service with catalog path
            services.AddSingleton<IAppService>(sp =>
            {
                var logger = sp.GetRequiredService<ILogger<AppService>>();
                var psExecutor = sp.GetRequiredService<PowerShellExecutor>();
                return new AppService(psExecutor, logger, GetDefaultCatalogPath());
            });
        }

        private static string GetDefaultCatalogPath()
        {
            // Try to find catalog relative to executable
            var assemblyDir = AppDomain.CurrentDomain.BaseDirectory;
            var paths = new[]
            {
                Path.Combine(assemblyDir, "..", "..", "..", "..", "better11", "apps", "catalog.json"),
                Path.Combine(assemblyDir, "catalog.json"),
                Path.Combine(Environment.CurrentDirectory, "catalog.json"),
                Path.Combine(Environment.CurrentDirectory, "better11", "apps", "catalog.json")
            };

            foreach (var path in paths)
            {
                var fullPath = Path.GetFullPath(path);
                if (File.Exists(fullPath))
                {
                    return fullPath;
                }
            }

            // Return default path even if not found
            return Path.Combine(assemblyDir, "catalog.json");
        }
    }
}
