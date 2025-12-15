using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Better11.GUI.Views;

namespace Better11.GUI
{
    /// <summary>
    /// Main application window with navigation.
    /// </summary>
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();
            
            // Set window properties
            Title = "Better11 - Windows Enhancement Toolkit";
            
            // Navigate to dashboard on startup
            ContentFrame.Navigate(typeof(DashboardPage));
            NavView.SelectedItem = NavView.MenuItems[0];
            NavView.Header = "Dashboard";
        }

        private void NavView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.IsSettingsSelected)
            {
                ContentFrame.Navigate(typeof(SettingsPage));
                NavView.Header = "Settings";
                return;
            }

            if (args.SelectedItem is NavigationViewItem item)
            {
                var tag = item.Tag?.ToString();
                NavView.Header = item.Content?.ToString() ?? "";
                
                switch (tag)
                {
                    case "Dashboard":
                        ContentFrame.Navigate(typeof(DashboardPage));
                        break;
                    case "Privacy":
                        ContentFrame.Navigate(typeof(PrivacyPage));
                        break;
                    case "Performance":
                        ContentFrame.Navigate(typeof(PerformancePage));
                        break;
                    case "Apps":
                        ContentFrame.Navigate(typeof(AppsPage));
                        break;
                    case "Network":
                        ContentFrame.Navigate(typeof(NetworkPage));
                        break;
                    case "Backup":
                        ContentFrame.Navigate(typeof(BackupPage));
                        break;
                    case "Shell":
                        ContentFrame.Navigate(typeof(ShellPage));
                        break;
                    case "Gaming":
                        ContentFrame.Navigate(typeof(GamingPage));
                        break;
                    case "Updates":
                        ContentFrame.Navigate(typeof(UpdatesPage));
                        break;
                    case "Drivers":
                        ContentFrame.Navigate(typeof(DriversPage));
                        break;
                    case "SystemInfo":
                        ContentFrame.Navigate(typeof(SystemInfoPage));
                        break;
                }
            }
        }
    }
}
