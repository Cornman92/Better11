using System.CommandLine;
using Better11.Core.Apps;
using Better11.Core.Deployment;
using Microsoft.Extensions.Logging;

namespace Better11.CLI;

class Program
{
    static async Task<int> Main(string[] args)
    {
        var catalogOption = new Option<FileInfo>(
            aliases: new[] { "--catalog", "-c" },
            description: "Path to the app catalog JSON")
        {
            IsRequired = false
        };

        var catalogPath = Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory,
            "..", "..", "..", "..", "..",
            "better11", "apps", "catalog.json");

        var rootCommand = new RootCommand("Better11 application manager")
        {
            catalogOption
        };

        // List command
        var listCommand = new Command("list", "List available applications");
        listCommand.SetHandler(async (FileInfo? catalog) =>
        {
            var catalogPath = catalog?.FullName ?? GetDefaultCatalogPath();
            var manager = new AppManager(catalogPath);
            var apps = manager.ListAvailable();
            foreach (var app in apps)
            {
                Console.WriteLine($"{app.AppId}: {app.Name} v{app.Version} ({app.InstallerType})");
            }
            return 0;
        }, catalogOption);
        rootCommand.AddCommand(listCommand);

        // Download command
        var downloadCommand = new Command("download", "Download an application");
        var downloadAppIdArgument = new Argument<string>("app_id", "Application ID to download");
        downloadCommand.AddArgument(downloadAppIdArgument);
        downloadCommand.AddOption(catalogOption);
        downloadCommand.SetHandler(async (string appId, FileInfo? catalog) =>
        {
            try
            {
                var catalogPath = catalog?.FullName ?? GetDefaultCatalogPath();
                var manager = new AppManager(catalogPath);
                var destination = await manager.DownloadAsync(appId);
                Console.WriteLine($"Downloaded to {destination}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Download failed: {ex.Message}");
                return 1;
            }
        }, downloadAppIdArgument, catalogOption);
        rootCommand.AddCommand(downloadCommand);

        // Install command
        var installCommand = new Command("install", "Download, verify, and install an application");
        var installAppIdArgument = new Argument<string>("app_id", "Application ID to install");
        installCommand.AddArgument(installAppIdArgument);
        installCommand.AddOption(catalogOption);
        installCommand.SetHandler(async (string appId, FileInfo? catalog) =>
        {
            try
            {
                var catalogPath = catalog?.FullName ?? GetDefaultCatalogPath();
                var manager = new AppManager(catalogPath);
                var (status, result) = await manager.InstallAsync(appId);
                var command = result.Command.Count > 0 ? string.Join(" ", result.Command) : "already installed";
                Console.WriteLine($"Installed {status.AppId} v{status.Version}: {command}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Installation failed: {ex.Message}");
                return 1;
            }
        }, installAppIdArgument, catalogOption);
        rootCommand.AddCommand(installCommand);

        // Uninstall command
        var uninstallCommand = new Command("uninstall", "Uninstall an installed application");
        var uninstallAppIdArgument = new Argument<string>("app_id", "Application ID to uninstall");
        uninstallCommand.AddArgument(uninstallAppIdArgument);
        uninstallCommand.AddOption(catalogOption);
        uninstallCommand.SetHandler((string appId, FileInfo? catalog) =>
        {
            try
            {
                var catalogPath = catalog?.FullName ?? GetDefaultCatalogPath();
                var manager = new AppManager(catalogPath);
                var result = manager.Uninstall(appId);
                Console.WriteLine($"Uninstalled via: {string.Join(" ", result.Command)}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Uninstall failed: {ex.Message}");
                return 1;
            }
        }, uninstallAppIdArgument, catalogOption);
        rootCommand.AddCommand(uninstallCommand);

        // Status command
        var statusCommand = new Command("status", "Show installation status");
        var statusAppIdArgument = new Argument<string?>("app_id", () => null, "Optional application ID");
        statusCommand.AddArgument(statusAppIdArgument);
        statusCommand.AddOption(catalogOption);
        statusCommand.SetHandler((string? appId, FileInfo? catalog) =>
        {
            var catalogPath = catalog?.FullName ?? GetDefaultCatalogPath();
            var manager = new AppManager(catalogPath);
            var statuses = manager.SummarizedStatus(appId);
            if (statuses.Count == 0)
            {
                Console.WriteLine("No status recorded");
                return 0;
            }
            foreach (var line in statuses)
            {
                Console.WriteLine(line);
            }
            return 0;
        }, statusAppIdArgument, catalogOption);
        rootCommand.AddCommand(statusCommand);

        // Deploy command
        var deployCommand = new Command("deploy", "Deployment utilities");
        var unattendCommand = new Command("unattend", "Generate a Windows unattend file");
        
        var productKeyOption = new Option<string>("--product-key", "Product key to embed in the answer file")
        {
            IsRequired = true
        };
        var outputOption = new Option<FileInfo>("--output", "Path to write unattend.xml")
        {
            IsRequired = true
        };
        var languageOption = new Option<string>("--language", () => "en-US", "UI language tag");
        var timezoneOption = new Option<string>("--timezone", () => "Pacific Standard Time", "Windows time zone name");
        var computerNameOption = new Option<string?>("--computer-name", "Optional computer name");
        var adminUserOption = new Option<string>("--admin-user", () => "Administrator", "Administrative account to create");
        var adminPasswordOption = new Option<string?>("--admin-password", "Password for the administrative account");
        var autoLogonOption = new Option<bool>("--auto-logon", "Enable automatic logon");
        var firstLogonCommandOption = new Option<List<string>>("--first-logon-command", "Add a synchronous first-logon command");
        var templateOption = new Option<string?>("--template", "Start from a predefined template (workstation, lab)");

        unattendCommand.AddOption(productKeyOption);
        unattendCommand.AddOption(outputOption);
        unattendCommand.AddOption(languageOption);
        unattendCommand.AddOption(timezoneOption);
        unattendCommand.AddOption(computerNameOption);
        unattendCommand.AddOption(adminUserOption);
        unattendCommand.AddOption(adminPasswordOption);
        unattendCommand.AddOption(autoLogonOption);
        unattendCommand.AddOption(firstLogonCommandOption);
        unattendCommand.AddOption(templateOption);

        unattendCommand.SetHandler(async (string productKey, FileInfo output, string language, string timezone,
            string? computerName, string adminUser, string? adminPassword, bool autoLogon,
            List<string> firstLogonCommands, string? template) =>
        {
            try
            {
                var builder = CreateUnattendBuilder(
                    template, productKey, adminUser, adminPassword, language, timezone, computerName, autoLogon, firstLogonCommands);
                
                var outputPath = builder.Export(output.FullName);
                Console.WriteLine($"Wrote unattend file to {outputPath}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Failed to generate unattend file: {ex.Message}");
                return 1;
            }
        }, productKeyOption, outputOption, languageOption, timezoneOption, computerNameOption,
            adminUserOption, adminPasswordOption, autoLogonOption, firstLogonCommandOption, templateOption);

        deployCommand.AddCommand(unattendCommand);
        rootCommand.AddCommand(deployCommand);

        return await rootCommand.InvokeAsync(args);
    }

    private static string GetDefaultCatalogPath()
    {
        var baseDir = AppDomain.CurrentDomain.BaseDirectory;
        var catalogPath = Path.Combine(
            baseDir,
            "..", "..", "..", "..", "..",
            "better11", "apps", "catalog.json");
        return Path.GetFullPath(catalogPath);
    }

    private static UnattendBuilder CreateUnattendBuilder(
        string? template, string productKey, string adminUser, string? adminPassword,
        string language, string timezone, string? computerName, bool autoLogon,
        List<string> firstLogonCommands)
    {
        UnattendBuilder builder;

        if (template == "workstation")
        {
            builder = UnattendBuilder.WorkstationTemplate(
                productKey: productKey,
                adminUser: adminUser,
                adminPassword: adminPassword,
                language: language,
                timeZone: timezone);
        }
        else if (template == "lab")
        {
            builder = UnattendBuilder.LabTemplate(
                productKey: productKey,
                language: language,
                timeZone: timezone);
        }
        else
        {
            builder = new UnattendBuilder(
                language: language,
                timeZone: timezone,
                computerName: computerName);
            builder.SetProductKey(productKey);
            if (adminPassword != null)
            {
                builder.SetAdminPassword(adminPassword);
            }
            builder.AddLocalAccount(adminUser, password: adminPassword, autoLogon: autoLogon);
        }

        foreach (var cmd in firstLogonCommands)
        {
            var parsed = ParseFirstLogonCommand(cmd);
            builder.AddFirstLogonCommand(
                order: parsed.Order,
                command: parsed.Command,
                description: parsed.Description);
        }

        return builder;
    }

    private static (int Order, string Command, string? Description) ParseFirstLogonCommand(string raw)
    {
        var order = 1;
        var description = (string?)null;
        var text = raw.Trim();

        if (text.Contains(':'))
        {
            var parts = text.Split(':', 2);
            if (int.TryParse(parts[0], out var parsedOrder))
            {
                order = parsedOrder;
                text = parts[1].Trim();
            }
        }

        if (text.Contains('|'))
        {
            var parts = text.Split('|', 2);
            description = parts[0].Trim();
            text = parts[1].Trim();
        }

        return (order, text, description);
    }
}
