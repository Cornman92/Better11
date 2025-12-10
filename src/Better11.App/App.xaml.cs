using Better11.Infrastructure.Logging;
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
                // Configure logging
                services.ConfigureLogging();

                // TODO: Register services here
                // services.AddSingleton<INavigationService, NavigationService>();
                // services.AddSingleton<IDialogService, DialogService>();
                // services.AddTransient<DashboardViewModel>();
                // etc.

                // Register main window
                services.AddSingleton<MainWindow>();
            })
            .Build();

        Log.Information("Better11 application initialized");
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
