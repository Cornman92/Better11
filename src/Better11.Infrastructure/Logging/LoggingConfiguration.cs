using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Serilog;
using Serilog.Events;

namespace Better11.Infrastructure.Logging;

/// <summary>
/// Configuration for application logging using Serilog.
/// </summary>
public static class LoggingConfiguration
{
    /// <summary>
    /// Configures Serilog logging for the application.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="logDirectory">The directory where log files will be stored.</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection ConfigureLogging(this IServiceCollection services, string? logDirectory = null)
    {
        // Set default log directory if not provided
        logDirectory ??= Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Better11",
            "Logs");

        // Ensure log directory exists
        Directory.CreateDirectory(logDirectory);

        // Configure Serilog
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
            .MinimumLevel.Override("System", LogEventLevel.Information)
            .Enrich.FromLogContext()
            .Enrich.WithThreadId()
            .Enrich.WithMachineName()
            .Enrich.WithEnvironmentName()
            .WriteTo.Console(
                outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
            .WriteTo.File(
                path: Path.Combine(logDirectory, "better11-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 30,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] [{SourceContext}] {Message:lj}{NewLine}{Exception}",
                shared: true)
            .WriteTo.Debug(
                outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
            .CreateLogger();

        // Add Serilog to the logging pipeline
        services.AddLogging(builder =>
        {
            builder.ClearProviders();
            builder.AddSerilog(dispose: true);
        });

        Log.Information("Better11 logging configured. Log directory: {LogDirectory}", logDirectory);

        return services;
    }

    /// <summary>
    /// Closes and flushes the Serilog logger on application shutdown.
    /// </summary>
    public static void CloseAndFlush()
    {
        Log.CloseAndFlush();
    }
}
