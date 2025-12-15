using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace Better11.WinUI.Views
{
    public sealed partial class MainWindow : Window
    {
        public MainViewModel ViewModel { get; }

        public MainWindow(MainViewModel viewModel)
        {
            ViewModel = viewModel;
            InitializeComponent();
            
            // Set initial page
            ContentFrame.Navigate(typeof(ApplicationsPage));
        }

        private void NavigationView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.IsSettingsSelected)
            {
                ContentFrame.Navigate(typeof(SettingsPage));
            }
            else if (args.SelectedItemContainer is NavigationViewItem item)
            {
                var tag = item.Tag?.ToString() ?? string.Empty;
                
                switch (tag)
                {
                    case "applications":
                        ContentFrame.Navigate(typeof(ApplicationsPage));
                        break;
                    case "systemtools":
                        ContentFrame.Navigate(typeof(SystemToolsPage));
                        break;
                    case "windowsupdates":
                        ContentFrame.Navigate(typeof(WindowsUpdatesPage));
                        break;
                    case "privacy":
                        ContentFrame.Navigate(typeof(PrivacyPage));
                        break;
                    case "startup":
                        ContentFrame.Navigate(typeof(StartupPage));
                        break;
                    case "performance":
                        ContentFrame.Navigate(typeof(PerformancePage));
                        break;
                    case "features":
                        // ContentFrame.Navigate(typeof(FeaturesPage));
                        break;
                }
            }
        }
    }
}
