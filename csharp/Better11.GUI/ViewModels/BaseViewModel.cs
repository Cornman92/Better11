using CommunityToolkit.Mvvm.ComponentModel;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Base class for all ViewModels.
    /// </summary>
    public abstract partial class BaseViewModel : ObservableObject
    {
        [ObservableProperty]
        private bool _isLoading;

        [ObservableProperty]
        private string _statusMessage = string.Empty;

        [ObservableProperty]
        private bool _hasError;

        protected void SetError(string message)
        {
            StatusMessage = message;
            HasError = true;
        }

        protected void ClearError()
        {
            StatusMessage = string.Empty;
            HasError = false;
        }

        protected void SetStatus(string message)
        {
            StatusMessage = message;
            HasError = false;
        }
    }
}
