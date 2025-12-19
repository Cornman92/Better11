using Better11.App.Helpers;
using Better11.App.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.UI.Xaml;
using Serilog;

namespace Better11.App;

/// <summary>
/// Provides application-specific behavior to supplement the default Application class.
/// </summary>
public partial class App : Application
{
    private Window? _mainWindow;
    private readonly IHost _host;

    /// <summary>
    /// Initializes the singleton application object.
    /// </summary>
    public App()
    {
        InitializeComponent();

        // Build host with dependency injection
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                // Configure all services using ServiceConfiguration
                services.ConfigureServices();
            })
            .Build();

        // Register global exception handler
        UnhandledException += OnUnhandledException;

        Log.Information("Better11 application initialized");
    }

    /// <summary>
    /// Handle unhandled exceptions.
    /// </summary>
    private void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
        var errorHandler = _host.Services.GetRequiredService<IErrorHandlingService>();
        errorHandler.HandleException(e.Exception, "Global");

        // Mark as handled to prevent crash (use with caution in production)
        e.Handled = true;

        Log.Error(e.Exception, "Unhandled exception occurred");
    }

    /// <summary>
    /// Invoked when the application is launched.
    /// </summary>
    /// <param name="args">Details about the launch request and process.</param>
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        Log.Information("Better11 application launching");

        // Get main window from DI container
        _mainWindow = _host.Services.GetRequiredService<MainWindow>();
        _mainWindow.Activate();

        Log.Information("Better11 main window activated");
    }

    /// <summary>
    /// Gets the current application instance.
    /// </summary>
    public new static App Current => (App)Application.Current;

    /// <summary>
    /// Gets the service provider for dependency injection.
    /// </summary>
    public IServiceProvider Services => _host.Services;
}
