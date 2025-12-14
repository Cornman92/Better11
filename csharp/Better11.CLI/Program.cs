using System;
using System.CommandLine;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Better11.Core.Interfaces;
using Better11.Core.Services;
using Better11.Core.PowerShell;
using Better11.CLI.Commands;
using Spectre.Console;

namespace Better11.CLI
{
    class Program
    {
        static async Task<int> Main(string[] args)
        {
            // Setup dependency injection
            var services = new ServiceCollection();
            ConfigureServices(services);
            var serviceProvider = services.BuildServiceProvider();

            // Create root command
            var rootCommand = new RootCommand("Better11 - Windows Enhancement Toolkit");

            // Add subcommands
            var appCommands = new AppCommands(serviceProvider);
            var systemCommands = new SystemCommands(serviceProvider);
            var privacyCommands = new PrivacyCommands(serviceProvider);
            var startupCommands = new StartupCommands(serviceProvider);

            rootCommand.AddCommand(appCommands.CreateCommand());
            rootCommand.AddCommand(systemCommands.CreateCommand());
            rootCommand.AddCommand(privacyCommands.CreateCommand());
            rootCommand.AddCommand(startupCommands.CreateCommand());

            // Execute
            return await rootCommand.InvokeAsync(args);
        }

        static void ConfigureServices(IServiceCollection services)
        {
            // Logging
            services.AddLogging(builder =>
            {
                builder.AddConsole();
                builder.SetMinimumLevel(LogLevel.Information);
            });

            // PowerShell
            services.AddSingleton<PowerShellExecutor>();

            // Services
            services.AddSingleton<IAppManagerService, AppManagerService>();
            services.AddSingleton<ISystemToolsService, SystemToolsService>();
            services.AddSingleton<IPrivacyService, PrivacyService>();
            services.AddSingleton<IStartupService, StartupService>();
            services.AddSingleton<IFeaturesService, FeaturesService>();
            services.AddSingleton<IUpdateService, UpdateService>();
            services.AddSingleton<IDiskService, DiskService>();
            services.AddSingleton<INetworkService, NetworkService>();
            services.AddSingleton<IBackupService, BackupService>();
            services.AddSingleton<IPowerService, PowerService>();
        }
    }
}
