namespace Better11.App.Services;

/// <summary>
/// Service for displaying dialogs and messages to the user.
/// </summary>
public interface IDialogService
{
    /// <summary>
    /// Shows an information message to the user.
    /// </summary>
    /// <param name="message">The message to display.</param>
    /// <param name="title">The title of the dialog.</param>
    Task ShowInfoAsync(string message, string title = "Information");

    /// <summary>
    /// Shows a warning message to the user.
    /// </summary>
    /// <param name="message">The message to display.</param>
    /// <param name="title">The title of the dialog.</param>
    Task ShowWarningAsync(string message, string title = "Warning");

    /// <summary>
    /// Shows an error message to the user.
    /// </summary>
    /// <param name="message">The message to display.</param>
    /// <param name="title">The title of the dialog.</param>
    Task ShowErrorAsync(string message, string title = "Error");

    /// <summary>
    /// Shows a confirmation dialog to the user.
    /// </summary>
    /// <param name="message">The message to display.</param>
    /// <param name="title">The title of the dialog.</param>
    /// <returns>True if the user confirmed; otherwise, false.</returns>
    Task<bool> ShowConfirmationAsync(string message, string title = "Confirm");

    /// <summary>
    /// Shows a file picker dialog.
    /// </summary>
    /// <param name="fileTypes">The file types to filter.</param>
    /// <returns>The selected file path, or null if cancelled.</returns>
    Task<string?> ShowFilePickerAsync(params string[] fileTypes);

    /// <summary>
    /// Shows a folder picker dialog.
    /// </summary>
    /// <returns>The selected folder path, or null if cancelled.</returns>
    Task<string?> ShowFolderPickerAsync();
}
