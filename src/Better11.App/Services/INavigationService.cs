namespace Better11.App.Services;

/// <summary>
/// Service for handling navigation between views in the application.
/// </summary>
public interface INavigationService
{
    /// <summary>
    /// Gets a value indicating whether the navigation can go back.
    /// </summary>
    bool CanGoBack { get; }

    /// <summary>
    /// Navigates to the specified page.
    /// </summary>
    /// <param name="pageKey">The unique key of the page to navigate to.</param>
    /// <param name="parameter">Optional parameter to pass to the page.</param>
    /// <returns>True if navigation was successful; otherwise, false.</returns>
    bool NavigateTo(string pageKey, object? parameter = null);

    /// <summary>
    /// Navigates back to the previous page.
    /// </summary>
    /// <returns>True if navigation was successful; otherwise, false.</returns>
    bool GoBack();

    /// <summary>
    /// Sets the navigation frame for the service.
    /// </summary>
    /// <param name="frame">The frame to use for navigation.</param>
    void SetFrame(object frame);
}
