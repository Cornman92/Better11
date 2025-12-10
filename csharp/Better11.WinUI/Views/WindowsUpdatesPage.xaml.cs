using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.WinUI.Views
{
    public sealed partial class WindowsUpdatesPage : Page
    {
        public WindowsUpdatesViewModel ViewModel { get; }

        public WindowsUpdatesPage()
        {
            ViewModel = App.GetService<WindowsUpdatesViewModel>();
            InitializeComponent();
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            await ViewModel.InitializeAsync();
        }
    }
}
