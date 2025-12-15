using Microsoft.UI.Xaml;
using Serilog;

namespace Better11.App;

/// <summary>
/// The main window for the Better11 application.
/// </summary>
public sealed partial class MainWindow : Window
{
    /// <summary>
    /// Initializes a new instance of the <see cref="MainWindow"/> class.
    /// </summary>
    public MainWindow()
    {
        InitializeComponent();
        Log.Information("Main window initialized");

        // Set window properties
        Title = "Better11";

        // TODO: Set up window size and position from settings
        // TODO: Set up window title bar customization
    }
}
