using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;

namespace Better11.App.Views;

/// <summary>
/// App Manager view for searching and installing applications.
/// </summary>
public sealed partial class AppManagerView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="AppManagerView"/> class.
    /// </summary>
    public AppManagerView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<AppManagerViewModel>();

        // Initialize the ViewModel
        _ = ViewModel.InitializeAsync();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public AppManagerViewModel ViewModel => (AppManagerViewModel)DataContext;

    /// <summary>
    /// Handle Enter key in search box.
    /// </summary>
    private void SearchBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == Windows.System.VirtualKey.Enter)
        {
            _ = ViewModel.SearchAppsCommand.ExecuteAsync(null);
        }
    }

    /// <summary>
    /// Handle package manager radio button changes.
    /// </summary>
    private void PackageManager_Changed(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
        if (WingetRadio.IsChecked == true)
        {
            ViewModel.SelectedPackageManager = "winget";
        }
        else if (ChocoRadio.IsChecked == true)
        {
            ViewModel.SelectedPackageManager = "choco";
        }
    }
}
