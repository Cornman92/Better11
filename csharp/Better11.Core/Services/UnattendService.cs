using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for generating Windows unattend XML files.
    /// </summary>
    public class UnattendService : IUnattendService
    {
        private readonly ILogger<UnattendService> _logger;
        
        private const string UnattendNS = "urn:schemas-microsoft-com:unattend";
        private const string WcmNS = "http://schemas.microsoft.com/WMIConfig/2002/State";

        public UnattendService(ILogger<UnattendService> logger)
        {
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<string> GenerateUnattendAsync(UnattendConfiguration configuration, string outputPath)
        {
            var validationError = ValidateConfiguration(configuration);
            if (validationError != null)
            {
                throw new ArgumentException(validationError);
            }

            _logger.LogInformation("Generating unattend file: {Path}", outputPath);

            var xml = BuildUnattendXml(configuration);

            // Ensure directory exists
            var directory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            await File.WriteAllTextAsync(outputPath, xml, Encoding.UTF8);
            
            _logger.LogInformation("Unattend file generated successfully");
            return outputPath;
        }

        /// <inheritdoc/>
        public UnattendConfiguration CreateWorkstationTemplate(
            string productKey,
            string adminUser = "Administrator",
            string? adminPassword = null,
            string language = "en-US",
            string timeZone = "Pacific Standard Time")
        {
            var config = new UnattendConfiguration
            {
                ProductKey = productKey,
                Language = language,
                InputLocale = language,
                TimeZone = timeZone,
                AdminPassword = adminPassword,
                Accounts = new()
                {
                    new LocalAccount(adminUser, adminPassword, true)
                },
                FirstLogonCommands = new()
                {
                    new FirstLogonCommand(1, 
                        "PowerShell -ExecutionPolicy Bypass -Command \"Write-Host 'Deployment ready'\"", 
                        "Confirm deployment readiness")
                }
            };

            return config;
        }

        /// <inheritdoc/>
        public UnattendConfiguration CreateLabTemplate(
            string productKey,
            string language = "en-US",
            string timeZone = "UTC")
        {
            var config = new UnattendConfiguration
            {
                ProductKey = productKey,
                Language = language,
                InputLocale = language,
                TimeZone = timeZone,
                Accounts = new()
                {
                    new LocalAccount("LabAdmin", "P@ssw0rd!", true)
                },
                FirstLogonCommands = new()
                {
                    new FirstLogonCommand(1,
                        "PowerShell -Command \"Get-ComputerInfo | Out-File C:\\setup.log\"",
                        "Capture baseline inventory")
                }
            };

            return config;
        }

        /// <inheritdoc/>
        public string? ValidateConfiguration(UnattendConfiguration configuration)
        {
            if (string.IsNullOrWhiteSpace(configuration.ProductKey))
                return "Product key is required";

            if (string.IsNullOrWhiteSpace(configuration.Language))
                return "Language must be specified";

            if (string.IsNullOrWhiteSpace(configuration.TimeZone))
                return "Time zone must be specified";

            if (configuration.Accounts.Count == 0)
                return "At least one local account is required";

            foreach (var account in configuration.Accounts)
            {
                if (string.IsNullOrWhiteSpace(account.Name))
                    return "Account name cannot be empty";
            }

            foreach (var command in configuration.FirstLogonCommands)
            {
                if (command.Order < 1)
                    return "Command order must be 1 or greater";
                if (string.IsNullOrWhiteSpace(command.Command))
                    return "Command text cannot be empty";
            }

            return null;
        }

        private string BuildUnattendXml(UnattendConfiguration config)
        {
            var settings = new XmlWriterSettings
            {
                Indent = true,
                IndentChars = "  ",
                Encoding = Encoding.UTF8
            };

            using var stringWriter = new StringWriter();
            using (var writer = XmlWriter.Create(stringWriter, settings))
            {
                writer.WriteStartDocument();
                
                // Root element
                writer.WriteStartElement("unattend", UnattendNS);
                writer.WriteAttributeString("xmlns", "wcm", null, WcmNS);

                // Windows PE pass
                WriteWindowsPEPass(writer, config);

                // Specialize pass
                WriteSpecializePass(writer, config);

                // OOBE System pass
                WriteOOBESystemPass(writer, config);

                writer.WriteEndElement(); // unattend
                writer.WriteEndDocument();
            }

            return stringWriter.ToString();
        }

        private void WriteWindowsPEPass(XmlWriter writer, UnattendConfiguration config)
        {
            writer.WriteStartElement("settings", UnattendNS);
            writer.WriteAttributeString("pass", "windowsPE");

            // International settings
            WriteComponent(writer, "Microsoft-Windows-International-Core-WinPE", w =>
            {
                WriteElement(w, "InputLocale", config.InputLocale);
                WriteElement(w, "SystemLocale", config.Language);
                WriteElement(w, "UILanguage", config.Language);
                WriteElement(w, "UserLocale", config.Language);
            });

            // Setup
            WriteComponent(writer, "Microsoft-Windows-Setup", w =>
            {
                w.WriteStartElement("UserData", UnattendNS);
                WriteElement(w, "AcceptEula", config.AcceptEula.ToString().ToLower());
                
                w.WriteStartElement("ProductKey", UnattendNS);
                WriteElement(w, "Key", config.ProductKey!);
                w.WriteEndElement(); // ProductKey
                
                w.WriteEndElement(); // UserData
            });

            writer.WriteEndElement(); // settings
        }

        private void WriteSpecializePass(XmlWriter writer, UnattendConfiguration config)
        {
            writer.WriteStartElement("settings", UnattendNS);
            writer.WriteAttributeString("pass", "specialize");

            WriteComponent(writer, "Microsoft-Windows-Shell-Setup", w =>
            {
                if (!string.IsNullOrEmpty(config.ComputerName))
                {
                    WriteElement(w, "ComputerName", config.ComputerName);
                }
                WriteElement(w, "TimeZone", config.TimeZone);
            });

            writer.WriteEndElement(); // settings
        }

        private void WriteOOBESystemPass(XmlWriter writer, UnattendConfiguration config)
        {
            writer.WriteStartElement("settings", UnattendNS);
            writer.WriteAttributeString("pass", "oobeSystem");

            WriteComponent(writer, "Microsoft-Windows-Shell-Setup", w =>
            {
                // OOBE settings
                w.WriteStartElement("OOBE", UnattendNS);
                WriteElement(w, "HideEULAPage", "true");
                WriteElement(w, "NetworkLocation", "Work");
                WriteElement(w, "ProtectYourPC", "3");
                w.WriteEndElement(); // OOBE

                // User Accounts
                w.WriteStartElement("UserAccounts", UnattendNS);

                if (!string.IsNullOrEmpty(config.AdminPassword))
                {
                    w.WriteStartElement("AdministratorPassword", UnattendNS);
                    WriteElement(w, "Value", config.AdminPassword);
                    WriteElement(w, "PlainText", "true");
                    w.WriteEndElement(); // AdministratorPassword
                }

                w.WriteStartElement("LocalAccounts", UnattendNS);
                foreach (var account in config.Accounts)
                {
                    w.WriteStartElement("LocalAccount", UnattendNS);
                    w.WriteAttributeString("wcm", "action", WcmNS, "add");
                    
                    WriteElement(w, "Name", account.Name);
                    WriteElement(w, "Group", string.Join(";", account.Groups));
                    
                    if (!string.IsNullOrEmpty(account.DisplayName))
                    {
                        WriteElement(w, "DisplayName", account.DisplayName);
                    }
                    
                    if (!string.IsNullOrEmpty(account.Password))
                    {
                        w.WriteStartElement("Password", UnattendNS);
                        WriteElement(w, "Value", account.Password);
                        WriteElement(w, "PlainText", "true");
                        w.WriteEndElement(); // Password
                    }

                    w.WriteEndElement(); // LocalAccount
                }
                w.WriteEndElement(); // LocalAccounts

                w.WriteEndElement(); // UserAccounts

                // AutoLogon for accounts with auto_logon enabled
                foreach (var account in config.Accounts.Where(a => a.AutoLogon))
                {
                    w.WriteStartElement("AutoLogon", UnattendNS);
                    WriteElement(w, "Username", account.Name);
                    WriteElement(w, "Enabled", "true");
                    WriteElement(w, "LogonCount", "5");
                    
                    if (!string.IsNullOrEmpty(account.Password))
                    {
                        w.WriteStartElement("Password", UnattendNS);
                        WriteElement(w, "Value", account.Password);
                        WriteElement(w, "PlainText", "true");
                        w.WriteEndElement(); // Password
                    }
                    w.WriteEndElement(); // AutoLogon
                    break; // Only one auto-logon supported
                }

                // First Logon Commands
                if (config.FirstLogonCommands.Count > 0)
                {
                    w.WriteStartElement("FirstLogonCommands", UnattendNS);
                    foreach (var command in config.FirstLogonCommands.OrderBy(c => c.Order))
                    {
                        w.WriteStartElement("SynchronousCommand", UnattendNS);
                        w.WriteAttributeString("wcm", "action", WcmNS, "add");
                        
                        WriteElement(w, "Order", command.Order.ToString());
                        WriteElement(w, "CommandLine", command.Command);
                        
                        if (!string.IsNullOrEmpty(command.Description))
                        {
                            WriteElement(w, "Description", command.Description);
                        }
                        
                        w.WriteEndElement(); // SynchronousCommand
                    }
                    w.WriteEndElement(); // FirstLogonCommands
                }
            });

            writer.WriteEndElement(); // settings
        }

        private void WriteComponent(XmlWriter writer, string name, Action<XmlWriter> content)
        {
            writer.WriteStartElement("component", UnattendNS);
            writer.WriteAttributeString("name", name);
            writer.WriteAttributeString("processorArchitecture", "amd64");
            writer.WriteAttributeString("publicKeyToken", "31bf3856ad364e35");
            writer.WriteAttributeString("language", "neutral");
            writer.WriteAttributeString("versionScope", "nonSxS");
            
            content(writer);
            
            writer.WriteEndElement(); // component
        }

        private void WriteElement(XmlWriter writer, string name, string value)
        {
            writer.WriteStartElement(name, UnattendNS);
            writer.WriteString(value);
            writer.WriteEndElement();
        }
    }
}
