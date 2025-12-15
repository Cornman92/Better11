using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml.Controls;

namespace Better11.App.Views;

/// <summary>
/// Image Editor view for managing Windows images.
/// </summary>
public sealed partial class ImageEditorView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="ImageEditorView"/> class.
    /// </summary>
    public ImageEditorView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<ImageEditorViewModel>();

        // Initialize the ViewModel
        _ = ViewModel.InitializeAsync();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public ImageEditorViewModel ViewModel => (ImageEditorViewModel)DataContext;
}
