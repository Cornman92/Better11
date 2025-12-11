using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.WinUI.Views
{
    public sealed partial class ApplicationsPage : Page
    {
        public ApplicationsViewModel ViewModel { get; }

        public ApplicationsPage()
        {
            ViewModel = App.GetService<ApplicationsViewModel>();
            InitializeComponent();
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            await ViewModel.InitializeAsync();
        }
    }
}
