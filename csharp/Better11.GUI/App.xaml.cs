using Microsoft.UI.Xaml;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Better11.Core.PowerShell;
using Better11.Core.Interfaces;
using Better11.Core.Services;

namespace Better11.GUI
{
    /// <summary>
    /// Main application class.
    /// </summary>
    public partial class App : Application
    {
        private Window? _mainWindow;
        public static IServiceProvider Services { get; private set; } = null!;

        public App()
        {
            this.InitializeComponent();
            
            // Configure services
            var services = new ServiceCollection();
            ConfigureServices(services);
            Services = services.BuildServiceProvider();
        }

        private void ConfigureServices(IServiceCollection services)
        {
            // Logging
            services.AddLogging(builder =>
            {
                builder.SetMinimumLevel(LogLevel.Information);
                builder.AddConsole();
            });

            // PowerShell executor
            services.AddSingleton<PowerShellExecutor>();

            // Services
            services.AddTransient<IPrivacyService, PrivacyService>();
            services.AddTransient<IBackupService, BackupService>();
            services.AddTransient<INetworkService, NetworkService>();
            services.AddTransient<IPowerService, PowerService>();
            services.AddTransient<IStartupService, StartupService>();
            services.AddTransient<IDiskService, DiskService>();
            services.AddTransient<IAppService, AppService>();
            services.AddTransient<IGamingService, GamingService>();
            services.AddTransient<ISysInfoService, SysInfoService>();
            services.AddTransient<IPerformanceService, PerformanceService>();
            services.AddTransient<IShellService, ShellService>();
            services.AddTransient<IUpdatesService, UpdatesService>();
            services.AddTransient<IFeaturesService, FeaturesService>();
            services.AddTransient<IDriversService, DriversService>();
            services.AddTransient<ITasksService, TasksService>();
            services.AddTransient<ISafetyService, SafetyService>();

            // ViewModels
            services.AddTransient<ViewModels.MainViewModel>();
            services.AddTransient<ViewModels.DashboardViewModel>();
            services.AddTransient<ViewModels.PrivacyViewModel>();
            services.AddTransient<ViewModels.PerformanceViewModel>();
            services.AddTransient<ViewModels.AppsViewModel>();
            services.AddTransient<ViewModels.NetworkViewModel>();
            services.AddTransient<ViewModels.BackupViewModel>();
            services.AddTransient<ViewModels.SettingsViewModel>();
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            _mainWindow = new MainWindow();
            _mainWindow.Activate();
        }
    }
}
