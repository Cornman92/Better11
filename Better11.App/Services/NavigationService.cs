using Better11.App.ViewModels;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.App.Services;

/// <summary>
/// Service for handling navigation between views in the application.
/// </summary>
public class NavigationService : INavigationService
{
    private Frame? _frame;
    private readonly Dictionary<string, Type> _pages = new();

    /// <inheritdoc/>
    public bool CanGoBack => _frame?.CanGoBack ?? false;

    /// <summary>
    /// Registers a page type with a unique key.
    /// </summary>
    /// <param name="key">The unique key for the page.</param>
    /// <param name="pageType">The type of the page.</param>
    public void RegisterPage(string key, Type pageType)
    {
        _pages[key] = pageType;
    }

    /// <inheritdoc/>
    public void SetFrame(object frame)
    {
        if (frame is Frame f)
        {
            _frame = f;
            _frame.Navigated += OnNavigated;
        }
    }

    /// <inheritdoc/>
    public bool NavigateTo(string pageKey, object? parameter = null)
    {
        if (_frame == null)
        {
            throw new InvalidOperationException("Navigation frame has not been set. Call SetFrame first.");
        }

        if (!_pages.TryGetValue(pageKey, out var pageType))
        {
            throw new ArgumentException($"Page with key '{pageKey}' is not registered.");
        }

        return _frame.Navigate(pageType, parameter);
    }

    /// <inheritdoc/>
    public bool GoBack()
    {
        if (_frame == null || !_frame.CanGoBack)
        {
            return false;
        }

        _frame.GoBack();
        return true;
    }

    private async void OnNavigated(object sender, NavigationEventArgs e)
    {
        if (e.Content is FrameworkElement { DataContext: ViewModelBase viewModel })
        {
            await viewModel.OnNavigatedToAsync(e.Parameter);
        }

        // Handle previous page's ViewModel
        if (e.SourcePageType != null && _frame?.BackStack.Count > 0)
        {
            var previousEntry = _frame.BackStack[^1];
            // Could call OnNavigatedFromAsync on previous ViewModel here if needed
        }
    }
}
