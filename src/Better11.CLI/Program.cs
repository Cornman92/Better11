using Better11.Infrastructure.Logging;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;
using System.CommandLine;

namespace Better11.CLI;

/// <summary>
/// Entry point for the Better11 CLI application.
/// </summary>
internal class Program
{
    static async Task<int> Main(string[] args)
    {
        // Create root command
        var rootCommand = new RootCommand("Better11 - Windows 11 System Enhancer CLI");

        // Add version option
        var versionOption = new Option<bool>(
            aliases: new[] { "--version", "-v" },
            description: "Show version information");
        rootCommand.AddGlobalOption(versionOption);

        // Set root command handler
        rootCommand.SetHandler((bool showVersion) =>
        {
            if (showVersion)
            {
                Console.WriteLine("Better11 CLI v0.1.0-alpha");
                Console.WriteLine("A Windows 11 system enhancement suite");
                return;
            }

            Console.WriteLine("Better11 CLI - Use --help for available commands");
        }, versionOption);

        // Configure host and services
        using var host = CreateHostBuilder(args).Build();

        // Execute command
        try
        {
            return await rootCommand.InvokeAsync(args);
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "CLI application terminated unexpectedly");
            return 1;
        }
        finally
        {
            LoggingConfiguration.CloseAndFlush();
        }
    }

    /// <summary>
    /// Creates the host builder for the CLI application.
    /// </summary>
    private static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureServices((context, services) =>
            {
                // Configure logging
                services.ConfigureLogging();

                // TODO: Register services here as they are implemented
                // services.AddSingleton<IImageService, ImageService>();
                // services.AddSingleton<IAppService, AppService>();
                // etc.
            });
}
