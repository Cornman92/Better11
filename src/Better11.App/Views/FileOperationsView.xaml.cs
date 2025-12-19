using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;

namespace Better11.App.Views;

/// <summary>
/// File Operations view for batch file management.
/// </summary>
public sealed partial class FileOperationsView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="FileOperationsView"/> class.
    /// </summary>
    public FileOperationsView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<FileOperationsViewModel>();

        // Initialize the ViewModel
        _ = ViewModel.InitializeAsync();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public FileOperationsViewModel ViewModel => (FileOperationsViewModel)DataContext;
}
