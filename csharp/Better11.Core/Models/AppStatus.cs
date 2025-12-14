using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents the installation status of an application.
    /// </summary>
    public class AppStatus
    {
        public string AppId { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string InstallerPath { get; set; } = string.Empty;
        public bool Installed { get; set; }
        public List<string> DependenciesInstalled { get; set; } = new();
        public DateTime InstalledDate { get; set; }
    }
}
