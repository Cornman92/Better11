using System;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for Windows unattend file generation.
    /// </summary>
    public interface IUnattendService
    {
        /// <summary>
        /// Generates a Windows unattend XML file.
        /// </summary>
        /// <param name="configuration">Unattend configuration.</param>
        /// <param name="outputPath">Path to write the unattend file.</param>
        /// <returns>Path to the generated file.</returns>
        Task<string> GenerateUnattendAsync(UnattendConfiguration configuration, string outputPath);

        /// <summary>
        /// Creates a workstation template configuration.
        /// </summary>
        /// <param name="productKey">Windows product key.</param>
        /// <param name="adminUser">Administrator username.</param>
        /// <param name="adminPassword">Administrator password.</param>
        /// <param name="language">UI language.</param>
        /// <param name="timeZone">Time zone.</param>
        /// <returns>Configured unattend configuration.</returns>
        UnattendConfiguration CreateWorkstationTemplate(
            string productKey,
            string adminUser = "Administrator",
            string? adminPassword = null,
            string language = "en-US",
            string timeZone = "Pacific Standard Time");

        /// <summary>
        /// Creates a lab template configuration.
        /// </summary>
        /// <param name="productKey">Windows product key.</param>
        /// <param name="language">UI language.</param>
        /// <param name="timeZone">Time zone.</param>
        /// <returns>Configured unattend configuration.</returns>
        UnattendConfiguration CreateLabTemplate(
            string productKey,
            string language = "en-US",
            string timeZone = "UTC");

        /// <summary>
        /// Validates an unattend configuration.
        /// </summary>
        /// <param name="configuration">Configuration to validate.</param>
        /// <returns>Validation result message, or null if valid.</returns>
        string? ValidateConfiguration(UnattendConfiguration configuration);
    }
}
