using Better11.WinUI.ViewModels;
using Microsoft.UI.Xaml.Controls;

namespace Better11.WinUI.Views
{
    public sealed partial class SystemToolsPage : Page
    {
        public SystemToolsViewModel ViewModel { get; }

        public SystemToolsPage()
        {
            ViewModel = App.GetService<SystemToolsViewModel>();
            InitializeComponent();
        }
    }
}
