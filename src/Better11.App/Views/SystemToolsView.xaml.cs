using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;

namespace Better11.App.Views;

/// <summary>
/// System Tools view for managing Windows services, registry, and tasks.
/// </summary>
public sealed partial class SystemToolsView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="SystemToolsView"/> class.
    /// </summary>
    public SystemToolsView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<SystemToolsViewModel>();

        // Initialize the ViewModel
        _ = ViewModel.InitializeAsync();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public SystemToolsViewModel ViewModel => (SystemToolsViewModel)DataContext;
}
