using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;

namespace Better11.App.Views;

/// <summary>
/// Dashboard view showing system information and quick actions.
/// </summary>
public sealed partial class DashboardView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="DashboardView"/> class.
    /// </summary>
    public DashboardView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<DashboardViewModel>();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public DashboardViewModel ViewModel => (DashboardViewModel)DataContext;
}
