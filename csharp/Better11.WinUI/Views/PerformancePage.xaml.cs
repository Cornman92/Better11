using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace Better11.WinUI.Views
{
    public sealed partial class PerformancePage : Page
    {
        public PerformanceViewModel ViewModel { get; }

        public PerformancePage()
        {
            ViewModel = App.GetService<PerformanceViewModel>();
            InitializeComponent();
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            await ViewModel.InitializeAsync();
        }
    }
}
