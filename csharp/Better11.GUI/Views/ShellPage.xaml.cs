using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Better11.Core.Models;

namespace Better11.GUI.Views
{
    public sealed partial class ShellPage : Page
    {
        private readonly IShellService _shellService;
        private bool _isLoading = true;

        public ShellPage()
        {
            this.InitializeComponent();
            _shellService = App.Services.GetRequiredService<IShellService>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            _isLoading = true;
            LoadingBar.Visibility = Visibility.Visible;
            
            var settings = await _shellService.GetShellSettingsAsync();
            AlignmentComboBox.SelectedIndex = (int)settings.TaskbarAlignment;
            SearchModeComboBox.SelectedIndex = (int)settings.SearchMode;
            TaskViewToggle.IsOn = settings.TaskViewVisible;
            WidgetsToggle.IsOn = settings.WidgetsVisible;
            CopilotToggle.IsOn = settings.CopilotVisible;
            ClassicContextMenuToggle.IsOn = settings.ClassicContextMenu;
            
            LoadingBar.Visibility = Visibility.Collapsed;
            _isLoading = false;
        }

        private async void Win10Style_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _shellService.ApplyShellPresetAsync(ShellPreset.Windows10Style);
            StatusText.Text = "Windows 10 style applied";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Minimal_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _shellService.ApplyShellPresetAsync(ShellPreset.Minimal);
            StatusText.Text = "Minimal preset applied";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Default_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _shellService.ApplyShellPresetAsync(ShellPreset.Default);
            StatusText.Text = "Default settings restored";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Alignment_Changed(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetTaskbarAlignmentAsync((TaskbarAlignment)AlignmentComboBox.SelectedIndex);
            StatusText.Text = "Taskbar alignment changed";
        }

        private async void SearchMode_Changed(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetSearchModeAsync((SearchMode)SearchModeComboBox.SelectedIndex);
            StatusText.Text = "Search mode changed";
        }

        private async void TaskView_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetTaskViewVisibleAsync(TaskViewToggle.IsOn);
        }

        private async void Widgets_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetWidgetsVisibleAsync(WidgetsToggle.IsOn);
        }

        private async void Copilot_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetCopilotVisibleAsync(CopilotToggle.IsOn);
        }

        private async void ClassicContextMenu_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _shellService.SetClassicContextMenuAsync(ClassicContextMenuToggle.IsOn);
            StatusText.Text = ClassicContextMenuToggle.IsOn ? "Classic context menu enabled" : "Modern context menu restored";
        }

        private async void RestartExplorer_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _shellService.RestartExplorerAsync();
            StatusText.Text = "Explorer restarted";
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
