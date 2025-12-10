using Better11.Core.Interfaces;
using Better11.Core.PowerShell;
using Better11.Core.Services;
using Better11.WinUI.ViewModels;
using Better11.WinUI.Views;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;

namespace Better11.WinUI
{
    public partial class App : Application
    {
        private IHost? _host;
        private Window? _mainWindow;

        public App()
        {
            InitializeComponent();
            ConfigureServices();
        }

        private void ConfigureServices()
        {
            _host = Host.CreateDefaultBuilder()
                .ConfigureServices((context, services) =>
                {
                    // Register core services
                    services.AddSingleton<PowerShellExecutor>();
                    services.AddSingleton<IAppManager, AppManagerService>();
                    services.AddSingleton<ISystemToolsService, SystemToolsService>();
                    services.AddSingleton<ISecurityService, SecurityService>();

                    // Register view models
                    services.AddTransient<MainViewModel>();
                    services.AddTransient<ApplicationsViewModel>();
                    services.AddTransient<SystemToolsViewModel>();
                    services.AddTransient<PrivacyViewModel>();
                    services.AddTransient<WindowsUpdatesViewModel>();
                    services.AddTransient<SettingsViewModel>();

                    // Register views
                    services.AddTransient<MainWindow>();
                    services.AddTransient<ApplicationsPage>();
                    services.AddTransient<SystemToolsPage>();
                    services.AddTransient<PrivacyPage>();
                    services.AddTransient<WindowsUpdatesPage>();
                    services.AddTransient<SettingsPage>();
                })
                .Build();
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            _mainWindow = _host?.Services.GetRequiredService<MainWindow>();
            _mainWindow?.Activate();
        }

        public static T GetService<T>() where T : class
        {
            var app = (App)Current;
            return app._host?.Services.GetRequiredService<T>()
                ?? throw new InvalidOperationException($"Service {typeof(T)} not found");
        }
    }
}
