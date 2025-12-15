using Better11.App.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.App.Views;

/// <summary>
/// Shell page containing the main navigation for the application.
/// </summary>
public sealed partial class ShellPage : Page
{
    private readonly INavigationService _navigationService;

    /// <summary>
    /// Initializes a new instance of the <see cref="ShellPage"/> class.
    /// </summary>
    public ShellPage()
    {
        InitializeComponent();

        // Get navigation service from DI
        _navigationService = App.Current.Services.GetRequiredService<INavigationService>();
        _navigationService.SetFrame(ContentFrame);

        // Navigate to Dashboard by default
        _navigationService.NavigateTo("Dashboard");
    }

    /// <summary>
    /// Gets a value indicating whether navigation can go back.
    /// </summary>
    public bool CanGoBack => _navigationService.CanGoBack;

    private void NavigationViewControl_BackRequested(NavigationView sender, NavigationViewBackRequestedEventArgs args)
    {
        _navigationService.GoBack();
    }

    private void NavigationViewControl_ItemInvoked(NavigationView sender, NavigationViewItemInvokedEventArgs args)
    {
        if (args.IsSettingsInvoked)
        {
            _navigationService.NavigateTo("Settings");
        }
        else if (args.InvokedItemContainer is NavigationViewItem item && item.Tag is string tag)
        {
            _navigationService.NavigateTo(tag);
        }
    }
}
