using CommunityToolkit.Mvvm.ComponentModel;

namespace Better11.App.ViewModels;

/// <summary>
/// Base class for all ViewModels in the application.
/// Provides common functionality like property change notification and navigation lifecycle.
/// </summary>
public abstract class ViewModelBase : ObservableObject
{
    private bool _isBusy;
    private string _title = string.Empty;

    /// <summary>
    /// Gets or sets a value indicating whether the ViewModel is currently busy performing an operation.
    /// </summary>
    public bool IsBusy
    {
        get => _isBusy;
        set
        {
            if (SetProperty(ref _isBusy, value))
            {
                OnPropertyChanged(nameof(IsNotBusy));
            }
        }
    }

    /// <summary>
    /// Gets a value indicating whether the ViewModel is not busy.
    /// </summary>
    public bool IsNotBusy => !IsBusy;

    /// <summary>
    /// Gets or sets the title for this ViewModel.
    /// </summary>
    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }

    /// <summary>
    /// Called when the view is navigated to.
    /// </summary>
    /// <param name="parameter">Navigation parameter.</param>
    public virtual Task OnNavigatedToAsync(object? parameter)
    {
        return Task.CompletedTask;
    }

    /// <summary>
    /// Called when the view is navigated from.
    /// </summary>
    public virtual Task OnNavigatedFromAsync()
    {
        return Task.CompletedTask;
    }

    /// <summary>
    /// Called when the ViewModel is being initialized.
    /// </summary>
    public virtual Task InitializeAsync()
    {
        return Task.CompletedTask;
    }
}
