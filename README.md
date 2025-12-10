# Better11

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![.NET](https://img.shields.io/badge/.NET-8.0-purple.svg)](https://dotnet.microsoft.com/)
[![Windows](https://img.shields.io/badge/Windows-11-blue.svg)](https://www.microsoft.com/windows)
[![Status](https://img.shields.io/badge/status-planning-yellow.svg)](ROADMAP.md)

An all-around Windows 11 system enhancer that includes live and offline image editing, application management, file operations, and system optimization.

---

## 🎯 Project Vision

Better11 consolidates and enhances features from three proven Windows tools:
- **DeployForge** - Deployment and system configuration
- **SMRT-FYLZ** - Smart file management and organization
- **App Installer Pro v2** - Application downloading and installation

The result is a comprehensive, modern Windows 11 enhancement suite built with WinUI3, C#, and PowerShell.

---

## ✨ Key Features

### 🖼️ Windows Image Editor
- Mount and edit WIM/ISO files offline
- Live system editing capabilities
- Driver injection and management
- Windows feature enable/disable
- Update integration and slipstreaming
- Appx/MSIX package management
- Registry editing for offline images
- Unattend.xml creation and editing

### 📦 Application Manager
- Universal package search (Winget, Chocolatey, Scoop)
- Silent installation and automation
- Update management
- Installation profiles
- License tracking
- Portable app management

### 📁 File Operations
- Advanced duplicate file finder
- Bulk file operations
- Smart file organization
- Advanced search capabilities
- Metadata editing
- Compression management

### ⚡ System Optimization
- Performance tuning profiles
- Privacy controls
- Startup and service management
- Context menu editor
- Registry optimizer
- Disk cleanup tools

### 🚀 Additional Features
- System backup and restore
- Deployment and provisioning
- Developer tools integration
- WSL management
- Plugin system
- And much more!

See [FEATURES.md](FEATURES.md) for complete feature specifications.

---

## 🏗️ Technology Stack

- **UI Framework**: WinUI3 (Windows App SDK)
- **Architecture**: MVVM Pattern
- **Language**: C# 12 (.NET 8.0)
- **Scripting**: PowerShell 7+
- **Database**: SQLite
- **Logging**: Serilog
- **Dependency Injection**: Microsoft.Extensions.DependencyInjection

See [TECH_STACK.md](TECH_STACK.md) for detailed technology information.

---

## 📋 Project Status

**Current Phase**: Foundation & Planning

This project is in the planning and initial development phase. We are:
- ✅ Project structure defined
- ✅ Architecture designed
- ✅ Features specified
- ✅ Roadmap created
- ✅ Documentation completed
- ⏳ Foundation implementation (upcoming)

See [ROADMAP.md](ROADMAP.md) for detailed development timeline.

---

## 🚀 Getting Started

### For Users

Better11 is currently in development. Watch this repository for updates!

### For Developers

#### Prerequisites
- Windows 11 (Build 22621+)
- Visual Studio 2022 (v17.8+)
- .NET 8.0 SDK
- PowerShell 7.4+

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/Cornman92/Better11.git
cd Better11

# Build the solution (once implemented)
dotnet restore
dotnet build

# Run tests (once implemented)
dotnet test
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

---

## 📚 Documentation

### Project Documentation
- [Project Plan](PROJECT_PLAN.md) - Overall vision and objectives
- [Architecture](ARCHITECTURE.md) - Technical architecture and design
- [Features](FEATURES.md) - Feature specifications and requirements
- [Roadmap](ROADMAP.md) - Development timeline and milestones
- [Tech Stack](TECH_STACK.md) - Technology stack details
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Getting Started](GETTING_STARTED.md) - Development setup guide

### For Contributors
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- Check [Issues](https://github.com/Cornman92/Better11/issues) for tasks
- Look for `good first issue` labels
- Join discussions

---

## 🤝 Contributing

We welcome contributions! Better11 is an open-source project and we appreciate help from the community.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Areas We Need Help

- Core feature implementation
- Testing and QA
- Documentation
- UI/UX design
- PowerShell scripting
- Bug fixes

---

## 📅 Roadmap

### Phase 1: Foundation (Weeks 1-4)
- ✅ Project planning
- ⏳ Project structure setup
- ⏳ Core framework implementation
- ⏳ UI foundation

### Phase 2: Core Features (Weeks 5-12)
- Windows Image Editor
- Application Manager
- Basic file operations

### Phase 3: Advanced Features (Weeks 13-20)
- Live system editing
- System optimization tools
- Advanced file operations

### Phase 4: Polish & Integration (Weeks 21-24)
- Testing and bug fixes
- UI/UX refinement
- Documentation completion

### Phase 5: Beta & Release (Weeks 25-28)
- Beta testing
- Final adjustments
- Public release

See [ROADMAP.md](ROADMAP.md) for complete development timeline.

---

## 🎯 Project Goals

### Technical Goals
- Startup time < 2 seconds
- Memory usage < 150MB idle
- Clean, maintainable architecture
- Comprehensive test coverage (>80%)
- Excellent performance

### User Experience Goals
- Intuitive, modern UI
- Responsive and fast
- Comprehensive documentation
- Accessible to all users
- Regular updates

---

## 📖 Architecture

Better11 follows a clean, layered architecture:

```
┌─────────────────────────────────────┐
│      Presentation Layer (WinUI3)    │
├─────────────────────────────────────┤
│      ViewModel Layer (MVVM)         │
├─────────────────────────────────────┤
│      Service Layer (Business Logic) │
├─────────────────────────────────────┤
│      Core Layer (Domain Models)     │
├─────────────────────────────────────┤
│      Infrastructure Layer           │
└─────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture information.

---

## 🔒 Security

Security is a top priority for Better11. We implement:
- Code signing for all releases
- Secure credential storage
- Input validation and sanitization
- Regular security audits
- Principle of least privilege

Report security vulnerabilities to the maintainers privately.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Better11 builds upon the foundations of:
- **DeployForge** - Deployment and configuration tools
- **SMRT-FYLZ** - File management solutions
- **App Installer Pro v2** - Application installation automation

Special thanks to:
- Microsoft for WinUI3 and .NET
- The open-source community
- All contributors and supporters

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/Cornman92/Better11/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cornman92/Better11/discussions)
- **Documentation**: [docs/](docs/)

---

## 🌟 Star History

If you find Better11 useful, please consider giving it a star! ⭐

---

## 📊 Project Stats

![GitHub issues](https://img.shields.io/github/issues/Cornman92/Better11)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Cornman92/Better11)
![GitHub contributors](https://img.shields.io/github/contributors/Cornman92/Better11)
![GitHub last commit](https://img.shields.io/github/last-commit/Cornman92/Better11)

---

**Built with ❤️ for the Windows community**

---

**Status**: Planning Phase
**Version**: 0.1.0-planning
**Last Updated**: 2025-12-10
