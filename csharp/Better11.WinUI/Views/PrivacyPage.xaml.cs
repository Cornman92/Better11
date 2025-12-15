using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.WinUI.Views
{
    public sealed partial class PrivacyPage : Page
    {
        public PrivacyViewModel ViewModel { get; }

        public PrivacyPage()
        {
            ViewModel = App.GetService<PrivacyViewModel>();
            InitializeComponent();
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            await ViewModel.InitializeAsync();
        }
    }
}
