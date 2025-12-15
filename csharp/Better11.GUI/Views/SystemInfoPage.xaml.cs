using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;

namespace Better11.GUI.Views
{
    public sealed partial class SystemInfoPage : Page
    {
        private readonly ISysInfoService _sysInfoService;

        public SystemInfoPage()
        {
            this.InitializeComponent();
            _sysInfoService = App.Services.GetRequiredService<ISysInfoService>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            
            var summary = await _sysInfoService.GetSystemSummaryAsync();
            
            // System
            ComputerNameText.Text = summary.ComputerName;
            ManufacturerText.Text = summary.Manufacturer;
            ModelText.Text = summary.Model;
            SystemTypeText.Text = summary.SystemType;
            
            // Windows
            if (summary.Windows != null)
            {
                WindowsEditionText.Text = summary.Windows.Edition;
                WindowsVersionText.Text = summary.Windows.Version;
                WindowsBuildText.Text = summary.Windows.Build;
            }
            
            // CPU
            if (summary.CPU != null)
            {
                CPUNameText.Text = summary.CPU.Name;
                CPUCoresText.Text = $"{summary.CPU.Cores} cores, {summary.CPU.LogicalProcessors} threads";
                CPUSpeedText.Text = $"{summary.CPU.MaxClockMHz} MHz";
            }
            
            // Memory
            if (summary.Memory != null)
            {
                MemoryTotalText.Text = $"{summary.Memory.TotalGB:F1} GB";
                MemoryTypeText.Text = $"{summary.Memory.Type ?? "DDR"} @ {summary.Memory.SpeedMHz} MHz";
            }
            
            StatusText.Text = "System information loaded";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Export_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            
            var path = await _sysInfoService.ExportSystemInfoAsync();
            if (!string.IsNullOrEmpty(path))
            {
                StatusText.Text = $"Exported to {path}";
            }
            else
            {
                StatusText.Text = "Failed to export system info";
            }
            
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
