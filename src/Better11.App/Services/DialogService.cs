using Microsoft.UI.Xaml.Controls;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace Better11.App.Services;

/// <summary>
/// Service for displaying dialogs and messages to the user.
/// </summary>
public class DialogService : IDialogService
{
    private Window? _window;

    /// <summary>
    /// Sets the parent window for dialogs.
    /// </summary>
    /// <param name="window">The window to use as parent.</param>
    public void SetWindow(Window window)
    {
        _window = window;
    }

    /// <inheritdoc/>
    public async Task ShowInfoAsync(string message, string title = "Information")
    {
        var dialog = new ContentDialog
        {
            Title = title,
            Content = message,
            CloseButtonText = "OK",
            XamlRoot = _window?.Content.XamlRoot
        };

        await dialog.ShowAsync();
    }

    /// <inheritdoc/>
    public async Task ShowWarningAsync(string message, string title = "Warning")
    {
        var dialog = new ContentDialog
        {
            Title = title,
            Content = message,
            CloseButtonText = "OK",
            XamlRoot = _window?.Content.XamlRoot
        };

        await dialog.ShowAsync();
    }

    /// <inheritdoc/>
    public async Task ShowErrorAsync(string message, string title = "Error")
    {
        var dialog = new ContentDialog
        {
            Title = title,
            Content = message,
            CloseButtonText = "OK",
            XamlRoot = _window?.Content.XamlRoot
        };

        await dialog.ShowAsync();
    }

    /// <inheritdoc/>
    public async Task<bool> ShowConfirmationAsync(string message, string title = "Confirm")
    {
        var dialog = new ContentDialog
        {
            Title = title,
            Content = message,
            PrimaryButtonText = "Yes",
            SecondaryButtonText = "No",
            DefaultButton = ContentDialogButton.Secondary,
            XamlRoot = _window?.Content.XamlRoot
        };

        var result = await dialog.ShowAsync();
        return result == ContentDialogResult.Primary;
    }

    /// <inheritdoc/>
    public async Task<string?> ShowFilePickerAsync(params string[] fileTypes)
    {
        var picker = new FileOpenPicker();

        // Initialize with window handle
        if (_window != null)
        {
            var hwnd = WindowNative.GetWindowHandle(_window);
            InitializeWithWindow.Initialize(picker, hwnd);
        }

        // Add file types
        if (fileTypes.Length > 0)
        {
            foreach (var fileType in fileTypes)
            {
                picker.FileTypeFilter.Add(fileType.StartsWith(".") ? fileType : $".{fileType}");
            }
        }
        else
        {
            picker.FileTypeFilter.Add("*");
        }

        var file = await picker.PickSingleFileAsync();
        return file?.Path;
    }

    /// <inheritdoc/>
    public async Task<string?> ShowFolderPickerAsync()
    {
        var picker = new FolderPicker();

        // Initialize with window handle
        if (_window != null)
        {
            var hwnd = WindowNative.GetWindowHandle(_window);
            InitializeWithWindow.Initialize(picker, hwnd);
        }

        picker.FileTypeFilter.Add("*");

        var folder = await picker.PickSingleFolderAsync();
        return folder?.Path;
    }
}
