using Better11.App.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace Better11.App.Views;

/// <summary>
/// Settings view for configuring the application.
/// </summary>
public sealed partial class SettingsView : Page
{
    /// <summary>
    /// Initializes a new instance of the <see cref="SettingsView"/> class.
    /// </summary>
    public SettingsView()
    {
        InitializeComponent();

        // Get ViewModel from DI
        DataContext = App.Current.Services.GetRequiredService<SettingsViewModel>();
    }

    /// <summary>
    /// Gets the ViewModel for this view.
    /// </summary>
    public SettingsViewModel ViewModel => (SettingsViewModel)DataContext;

    /// <summary>
    /// Converts ElementTheme to RadioButton index.
    /// </summary>
    private int ThemeToIndex(ElementTheme theme)
    {
        return theme switch
        {
            ElementTheme.Light => 0,
            ElementTheme.Dark => 1,
            ElementTheme.Default => 2,
            _ => 2
        };
    }

    /// <summary>
    /// Converts RadioButton index to ElementTheme.
    /// </summary>
    private ElementTheme IndexToTheme(int index)
    {
        return index switch
        {
            0 => ElementTheme.Light,
            1 => ElementTheme.Dark,
            2 => ElementTheme.Default,
            _ => ElementTheme.Default
        };
    }
}
