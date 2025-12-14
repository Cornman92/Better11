using System.Xml;
using System.Xml.Linq;

namespace Better11.Core.Deployment;

/// <summary>
/// Builds a Windows unattend XML document.
/// </summary>
public class UnattendBuilder
{
    private readonly string _language;
    private readonly string _inputLocale;
    private readonly string _timeZone;
    private readonly string? _computerName;
    private string? _productKey;
    private bool _acceptEula = true;
    private string? _adminPassword;
    private readonly List<LocalAccount> _accounts = new();
    private readonly List<FirstLogonCommand> _firstLogon = new();

    private const string UnattendNs = "urn:schemas-microsoft-com:unattend";
    private const string WcmNs = "http://schemas.microsoft.com/WMIConfig/2002/State";
    private const string XsiNs = "http://www.w3.org/2001/XMLSchema-instance";

    public UnattendBuilder(
        string language = "en-US",
        string inputLocale = "en-US",
        string timeZone = "Pacific Standard Time",
        string? computerName = null)
    {
        _language = language;
        _inputLocale = inputLocale;
        _timeZone = timeZone;
        _computerName = computerName;
    }

    public static UnattendBuilder WorkstationTemplate(
        string productKey,
        string adminUser = "Administrator",
        string? adminPassword = null,
        string language = "en-US",
        string timeZone = "Pacific Standard Time")
    {
        var builder = new UnattendBuilder(language: language, timeZone: timeZone);
        builder.SetProductKey(productKey);
        builder.SetAdminPassword(adminPassword);
        builder.AddLocalAccount(adminUser, password: adminPassword, autoLogon: true);
        builder.AddFirstLogonCommand(
            order: 1,
            command: "PowerShell -ExecutionPolicy Bypass -Command \"Write-Host 'Deployment ready'\"",
            description: "Confirm deployment readiness");
        return builder;
    }

    public static UnattendBuilder LabTemplate(
        string productKey,
        string language = "en-US",
        string timeZone = "UTC")
    {
        var builder = new UnattendBuilder(language: language, timeZone: timeZone);
        builder.SetProductKey(productKey);
        builder.AddLocalAccount("LabAdmin", password: "P@ssw0rd!", autoLogon: true);
        builder.AddFirstLogonCommand(
            order: 1,
            command: "PowerShell -Command \"Get-ComputerInfo | Out-File C:\\setup.log\"",
            description: "Capture baseline inventory");
        return builder;
    }

    public UnattendBuilder SetProductKey(string productKey)
    {
        if (string.IsNullOrEmpty(productKey))
        {
            throw new ArgumentException("Product key is required", nameof(productKey));
        }
        _productKey = productKey;
        return this;
    }

    public UnattendBuilder SetAdminPassword(string? password)
    {
        if (password != null && password.Length == 0)
        {
            throw new ArgumentException("Administrator password cannot be an empty string", nameof(password));
        }
        _adminPassword = password;
        return this;
    }

    public UnattendBuilder AddLocalAccount(
        string name,
        string? password = null,
        string? displayName = null,
        IEnumerable<string>? groups = null,
        bool autoLogon = false)
    {
        if (string.IsNullOrEmpty(name))
        {
            throw new ArgumentException("Local account name is required", nameof(name));
        }

        var account = new LocalAccount
        {
            Name = name,
            Password = password,
            DisplayName = displayName,
            Groups = groups?.ToList() ?? new List<string> { "Administrators" },
            AutoLogon = autoLogon
        };

        if (account.Groups.Any(string.IsNullOrEmpty))
        {
            throw new ArgumentException("Group names must be non-empty");
        }

        _accounts.Add(account);
        return this;
    }

    public UnattendBuilder AddFirstLogonCommand(int order, string command, string? description = null)
    {
        if (order < 1)
        {
            throw new ArgumentException("Command order must be 1 or greater", nameof(order));
        }
        if (string.IsNullOrEmpty(command))
        {
            throw new ArgumentException("Command text is required", nameof(command));
        }

        _firstLogon.Add(new FirstLogonCommand
        {
            Order = order,
            Command = command,
            Description = description
        });
        return this;
    }

    private void Validate()
    {
        if (string.IsNullOrEmpty(_productKey))
        {
            throw new InvalidOperationException("Product key must be provided before building unattend.xml");
        }
        if (string.IsNullOrEmpty(_language))
        {
            throw new InvalidOperationException("Language must be specified");
        }
        if (string.IsNullOrEmpty(_timeZone))
        {
            throw new InvalidOperationException("Time zone must be specified");
        }
        if (_accounts.Count == 0)
        {
            throw new InvalidOperationException("At least one local account is required");
        }
    }

    public XDocument Build()
    {
        Validate();

        var ns = XNamespace.Get(UnattendNs);
        var wcm = XNamespace.Get(WcmNs);
        var xsi = XNamespace.Get(XsiNs);

        var root = new XElement(ns + "unattend");

        AppendWindowsPE(root, ns, wcm);
        AppendSpecialize(root, ns, wcm);
        AppendOobeSystem(root, ns, wcm);

        return new XDocument(root);
    }

    private void AppendWindowsPE(XElement root, XNamespace ns, XNamespace wcm)
    {
        var settings = new XElement(ns + "settings", new XAttribute("pass", "windowsPE"));

        var international = CreateComponent(settings, ns, wcm, "Microsoft-Windows-International-Core-WinPE");
        international.Add(new XElement(ns + "InputLocale", _inputLocale));
        international.Add(new XElement(ns + "SystemLocale", _language));
        international.Add(new XElement(ns + "UILanguage", _language));
        international.Add(new XElement(ns + "UserLocale", _language));
        settings.Add(international);

        var setup = CreateComponent(settings, ns, wcm, "Microsoft-Windows-Setup");
        var userData = new XElement(ns + "UserData");
        userData.Add(new XElement(ns + "AcceptEula", _acceptEula.ToString().ToLowerInvariant()));
        var productKey = new XElement(ns + "ProductKey");
        productKey.Add(new XElement(ns + "Key", _productKey));
        userData.Add(productKey);
        setup.Add(userData);
        settings.Add(setup);

        root.Add(settings);
    }

    private void AppendSpecialize(XElement root, XNamespace ns, XNamespace wcm)
    {
        var settings = new XElement(ns + "settings", new XAttribute("pass", "specialize"));
        var shellSetup = CreateComponent(settings, ns, wcm, "Microsoft-Windows-Shell-Setup");
        
        if (!string.IsNullOrEmpty(_computerName))
        {
            shellSetup.Add(new XElement(ns + "ComputerName", _computerName));
        }
        shellSetup.Add(new XElement(ns + "TimeZone", _timeZone));
        settings.Add(shellSetup);

        root.Add(settings);
    }

    private void AppendOobeSystem(XElement root, XNamespace ns, XNamespace wcm)
    {
        var settings = new XElement(ns + "settings", new XAttribute("pass", "oobeSystem"));
        var shellSetup = CreateComponent(settings, ns, wcm, "Microsoft-Windows-Shell-Setup");

        var oobe = new XElement(ns + "OOBE");
        oobe.Add(new XElement(ns + "HideEULAPage", "true"));
        oobe.Add(new XElement(ns + "NetworkLocation", "Work"));
        oobe.Add(new XElement(ns + "ProtectYourPC", "3"));
        shellSetup.Add(oobe);

        var userAccounts = new XElement(ns + "UserAccounts");
        if (!string.IsNullOrEmpty(_adminPassword))
        {
            var adminPw = new XElement(ns + "AdministratorPassword");
            adminPw.Add(new XElement(ns + "Value", _adminPassword));
            adminPw.Add(new XElement(ns + "PlainText", "true"));
            userAccounts.Add(adminPw);
        }

        var localAccounts = new XElement(ns + "LocalAccounts");
        foreach (var account in _accounts)
        {
            var localAccount = new XElement(ns + "LocalAccount",
                new XAttribute(wcm + "action", "add"));
            localAccount.Add(new XElement(ns + "Name", account.Name));
            localAccount.Add(new XElement(ns + "Group", string.Join(";", account.Groups)));
            
            if (!string.IsNullOrEmpty(account.DisplayName))
            {
                localAccount.Add(new XElement(ns + "DisplayName", account.DisplayName));
            }
            
            if (!string.IsNullOrEmpty(account.Password))
            {
                var password = new XElement(ns + "Password");
                password.Add(new XElement(ns + "Value", account.Password));
                password.Add(new XElement(ns + "PlainText", "true"));
                localAccount.Add(password);
            }

            localAccounts.Add(localAccount);

            if (account.AutoLogon)
            {
                var autoLogon = new XElement(ns + "AutoLogon");
                autoLogon.Add(new XElement(ns + "Username", account.Name));
                autoLogon.Add(new XElement(ns + "Enabled", "true"));
                autoLogon.Add(new XElement(ns + "LogonCount", "5"));
                
                if (!string.IsNullOrEmpty(account.Password))
                {
                    var password = new XElement(ns + "Password");
                    password.Add(new XElement(ns + "Value", account.Password));
                    password.Add(new XElement(ns + "PlainText", "true"));
                    autoLogon.Add(password);
                }
                
                shellSetup.Add(autoLogon);
            }
        }
        userAccounts.Add(localAccounts);
        shellSetup.Add(userAccounts);

        if (_firstLogon.Count > 0)
        {
            var commands = new XElement(ns + "FirstLogonCommands");
            foreach (var cmd in _firstLogon.OrderBy(c => c.Order))
            {
                var syncCmd = new XElement(ns + "SynchronousCommand",
                    new XAttribute(wcm + "action", "add"));
                syncCmd.Add(new XElement(ns + "Order", cmd.Order.ToString()));
                syncCmd.Add(new XElement(ns + "CommandLine", cmd.Command));
                if (!string.IsNullOrEmpty(cmd.Description))
                {
                    syncCmd.Add(new XElement(ns + "Description", cmd.Description));
                }
                commands.Add(syncCmd);
            }
            shellSetup.Add(commands);
        }

        root.Add(settings);
    }

    private XElement CreateComponent(XElement parent, XNamespace ns, XNamespace wcm, string name)
    {
        return new XElement(ns + "component",
            new XAttribute("name", name),
            new XAttribute("processorArchitecture", "amd64"),
            new XAttribute("publicKeyToken", "31bf3856ad364e35"),
            new XAttribute("language", "neutral"),
            new XAttribute("versionScope", "nonSxS"));
    }

    public string ToXmlString()
    {
        var doc = Build();
        var settings = new XmlWriterSettings
        {
            Indent = true,
            IndentChars = "  ",
            OmitXmlDeclaration = false,
            Encoding = System.Text.Encoding.UTF8
        };

        using var writer = new StringWriter();
        using var xmlWriter = XmlWriter.Create(writer, settings);
        doc.Save(xmlWriter);
        return writer.ToString();
    }

    public string Export(string outputPath)
    {
        var xmlContent = ToXmlString();
        var directory = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }
        File.WriteAllText(outputPath, xmlContent, System.Text.Encoding.UTF8);
        return outputPath;
    }
}

internal class LocalAccount
{
    public required string Name { get; init; }
    public string? Password { get; init; }
    public string? DisplayName { get; init; }
    public required List<string> Groups { get; init; }
    public bool AutoLogon { get; init; }
}

internal class FirstLogonCommand
{
    public required int Order { get; init; }
    public required string Command { get; init; }
    public string? Description { get; init; }
}
