using System;
using Better11.Core.Models;
using Xunit;

namespace Better11.Tests.Models
{
    public class UnattendModelsTests
    {
        [Fact]
        public void LocalAccount_Constructor_SetsProperties()
        {
            // Arrange & Act
            var account = new LocalAccount("TestUser", "Password123", true);

            // Assert
            Assert.Equal("TestUser", account.Name);
            Assert.Equal("Password123", account.Password);
            Assert.True(account.AutoLogon);
            Assert.Contains("Administrators", account.Groups);
        }

        [Fact]
        public void LocalAccount_Constructor_ThrowsOnEmptyName()
        {
            // Act & Assert
            Assert.Throws<ArgumentException>(() => new LocalAccount("", "password"));
            Assert.Throws<ArgumentException>(() => new LocalAccount("  ", "password"));
        }

        [Fact]
        public void FirstLogonCommand_Constructor_SetsProperties()
        {
            // Arrange & Act
            var command = new FirstLogonCommand(1, "echo Hello", "Test command");

            // Assert
            Assert.Equal(1, command.Order);
            Assert.Equal("echo Hello", command.Command);
            Assert.Equal("Test command", command.Description);
        }

        [Fact]
        public void FirstLogonCommand_Constructor_ThrowsOnInvalidOrder()
        {
            // Act & Assert
            Assert.Throws<ArgumentException>(() => new FirstLogonCommand(0, "echo Hello"));
            Assert.Throws<ArgumentException>(() => new FirstLogonCommand(-1, "echo Hello"));
        }

        [Fact]
        public void FirstLogonCommand_Constructor_ThrowsOnEmptyCommand()
        {
            // Act & Assert
            Assert.Throws<ArgumentException>(() => new FirstLogonCommand(1, ""));
            Assert.Throws<ArgumentException>(() => new FirstLogonCommand(1, "  "));
        }

        [Fact]
        public void UnattendConfiguration_HasDefaultValues()
        {
            // Arrange & Act
            var config = new UnattendConfiguration();

            // Assert
            Assert.Equal("en-US", config.Language);
            Assert.Equal("en-US", config.InputLocale);
            Assert.Equal("Pacific Standard Time", config.TimeZone);
            Assert.True(config.AcceptEula);
            Assert.Empty(config.Accounts);
            Assert.Empty(config.FirstLogonCommands);
        }
    }
}
