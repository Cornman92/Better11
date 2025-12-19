using Better11.App.Services;
using Better11.App.ViewModels;
using Better11.Core.Interfaces;
using Better11.Infrastructure.Configuration;
using Better11.Infrastructure.Logging;
using Better11.Services;
using Microsoft.Extensions.DependencyInjection;

namespace Better11.App.Helpers;

/// <summary>
/// Configuration for dependency injection services.
/// </summary>
public static class ServiceConfiguration
{
    /// <summary>
    /// Configures all services for the application.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <returns>The configured service collection.</returns>
    public static IServiceCollection ConfigureServices(this IServiceCollection services)
    {
        // Configure logging
        services.ConfigureLogging();

        // Register infrastructure services
        services.AddSingleton<IConfigurationService, ConfigurationService>();

        // Register core services
        services.AddSingleton<IFileSystemService, FileSystemService>();
        services.AddSingleton<IProcessService, ProcessService>();
        services.AddSingleton<ISecurityService, SecurityService>();
        services.AddSingleton<IPowerShellEngine, PowerShellEngine>();

        // Register app services
        services.AddSingleton<INavigationService>(provider =>
        {
            var navService = new NavigationService();

            // Register pages
            navService.RegisterPage("Dashboard", typeof(Views.DashboardView));
            navService.RegisterPage("Settings", typeof(Views.SettingsView));
            navService.RegisterPage("ImageEditor", typeof(Views.ImageEditorView));
            navService.RegisterPage("AppManager", typeof(Views.AppManagerView));
            navService.RegisterPage("FileOperations", typeof(Views.FileOperationsView));
            navService.RegisterPage("SystemTools", typeof(Views.SystemToolsView));
            // Add more page registrations as views are created

            return navService;
        });

        services.AddSingleton<IDialogService, DialogService>();
        services.AddSingleton<IErrorHandlingService, ErrorHandlingService>();

        // Register ViewModels
        services.AddTransient<DashboardViewModel>();
        services.AddTransient<SettingsViewModel>();
        services.AddTransient<ImageEditorViewModel>();
        services.AddTransient<AppManagerViewModel>();
        services.AddTransient<FileOperationsViewModel>();
        services.AddTransient<SystemToolsViewModel>();

        // Register main window
        services.AddSingleton<MainWindow>();

        return services;
    }
}
