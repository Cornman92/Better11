using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a local user account to be created during Windows setup.
    /// </summary>
    public class LocalAccount
    {
        public string Name { get; set; } = string.Empty;
        public string? Password { get; set; }
        public string? DisplayName { get; set; }
        public List<string> Groups { get; set; } = new() { "Administrators" };
        public bool AutoLogon { get; set; }

        public LocalAccount() { }

        public LocalAccount(string name, string? password = null, bool autoLogon = false)
        {
            if (string.IsNullOrWhiteSpace(name))
                throw new ArgumentException("Local account name is required", nameof(name));
            Name = name;
            Password = password;
            AutoLogon = autoLogon;
        }
    }

    /// <summary>
    /// Represents a synchronous first-logon command.
    /// </summary>
    public class FirstLogonCommand
    {
        public int Order { get; set; }
        public string Command { get; set; } = string.Empty;
        public string? Description { get; set; }

        public FirstLogonCommand() { }

        public FirstLogonCommand(int order, string command, string? description = null)
        {
            if (order < 1)
                throw new ArgumentException("Command order must be 1 or greater", nameof(order));
            if (string.IsNullOrWhiteSpace(command))
                throw new ArgumentException("Command text is required", nameof(command));
            Order = order;
            Command = command;
            Description = description;
        }
    }

    /// <summary>
    /// Configuration for Windows unattend XML generation.
    /// </summary>
    public class UnattendConfiguration
    {
        public string Language { get; set; } = "en-US";
        public string InputLocale { get; set; } = "en-US";
        public string TimeZone { get; set; } = "Pacific Standard Time";
        public string? ComputerName { get; set; }
        public string? ProductKey { get; set; }
        public bool AcceptEula { get; set; } = true;
        public string? AdminPassword { get; set; }
        public List<LocalAccount> Accounts { get; set; } = new();
        public List<FirstLogonCommand> FirstLogonCommands { get; set; } = new();
    }
}
