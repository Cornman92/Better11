using System;
using System.CommandLine;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.PowerShell;
using Better11.Core.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Better11.CLI;

class Program
{
    static async Task<int> Main(string[] args)
    {
        // Setup DI
        var services = new ServiceCollection();
        ConfigureServices(services);
        var serviceProvider = services.BuildServiceProvider();

        var rootCommand = new RootCommand("Better11 - Windows Enhancement Toolkit");

        // List Command
        var listCommand = new Command("list", "List available applications");
        listCommand.SetHandler(async () =>
        {
            try 
            {
                var appManager = serviceProvider.GetRequiredService<IAppManager>();
                var apps = await appManager.ListAvailableAppsAsync();
                foreach (var app in apps)
                {
                    Console.WriteLine($"{app.AppId}: {app.Name} v{app.Version} ({app.InstallerType})");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
            }
        });
        rootCommand.AddCommand(listCommand);

        // Install Command
        var installCommand = new Command("install", "Install an application");
        var appIdArgument = new Argument<string>("appId", "The application ID to install");
        var forceOption = new Option<bool>("--force", "Force installation");
        installCommand.AddArgument(appIdArgument);
        installCommand.AddOption(forceOption);
        installCommand.SetHandler(async (string appId, bool force) =>
        {
            try
            {
                var appManager = serviceProvider.GetRequiredService<IAppManager>();
                var result = await appManager.InstallAppAsync(appId, force);
                if (result.Success)
                {
                    Console.WriteLine($"Installed {result.AppId} v{result.Version}: {result.Status}");
                }
                else
                {
                    Console.Error.WriteLine($"Installation failed: {result.ErrorMessage}");
                }
            }
            catch (Exception ex)
            {
                 Console.Error.WriteLine($"Error: {ex.Message}");
            }
        }, appIdArgument, forceOption);
        rootCommand.AddCommand(installCommand);
        
        // Uninstall Command
        var uninstallCommand = new Command("uninstall", "Uninstall an application");
        var appIdUninstallArg = new Argument<string>("appId", "The application ID to uninstall");
        uninstallCommand.AddArgument(appIdUninstallArg);
        uninstallCommand.SetHandler(async (string appId) =>
        {
             try
             {
                 var appManager = serviceProvider.GetRequiredService<IAppManager>();
                 var result = await appManager.UninstallAppAsync(appId);
                 if (result.Success)
                 {
                     Console.WriteLine($"Uninstalled {result.AppId}");
                 }
                 else
                 {
                     Console.Error.WriteLine($"Uninstall failed: {result.ErrorMessage}");
                 }
             }
             catch (Exception ex)
             {
                 Console.Error.WriteLine($"Error: {ex.Message}");
             }
        }, appIdUninstallArg);
        rootCommand.AddCommand(uninstallCommand);

        // Status Command
        var statusCommand = new Command("status", "Show installation status");
        var appIdStatusArg = new Argument<string?>("appId", "Optional application ID");
        appIdStatusArg.SetDefaultValue(null);
        statusCommand.AddArgument(appIdStatusArg);
        statusCommand.SetHandler(async (string? appId) =>
        {
            try
            {
                var appManager = serviceProvider.GetRequiredService<IAppManager>();
                var statuses = await appManager.GetAppStatusAsync(appId);
                if (statuses.Count == 0)
                {
                    Console.WriteLine("No status recorded");
                    return;
                }
                foreach (var status in statuses)
                {
                    Console.WriteLine($"{status.AppId}: Installed={status.Installed} Version={status.Version}");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
            }
        }, appIdStatusArg);
        rootCommand.AddCommand(statusCommand);

        return await rootCommand.InvokeAsync(args);
    }

    static void ConfigureServices(IServiceCollection services)
    {
        services.AddLogging(configure =>
        {
            configure.AddConsole();
            configure.SetMinimumLevel(LogLevel.Warning); // Less verbose for CLI user
        });

        services.AddSingleton<PowerShellExecutor>();
        services.AddSingleton<IAppManager, AppManagerService>();
    }
}
