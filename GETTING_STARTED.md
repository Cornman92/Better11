# Getting Started with Better11 Development

This guide will help you get started with Better11 development, from setting up your environment to making your first contribution.

---

## Quick Start Checklist

- [ ] Install prerequisites
- [ ] Clone repository
- [ ] Set up development environment
- [ ] Build the solution
- [ ] Run the application
- [ ] Run tests
- [ ] Read documentation
- [ ] Make your first contribution

---

## Prerequisites

### Required Software

1. **Windows 11**
   - Build 22621 or higher
   - Windows 11 22H2 or later recommended
   - Administrator access for some features

2. **Visual Studio 2022**
   - Version 17.8 or higher
   - Download: [Visual Studio 2022 Community](https://visualstudio.microsoft.com/vs/)
   - Required workloads:
     - .NET Desktop Development
     - Universal Windows Platform Development

3. **.NET 8.0 SDK**
   - Download: [.NET 8.0](https://dotnet.microsoft.com/download/dotnet/8.0)
   - Verify installation: `dotnet --version`

4. **Windows 11 SDK**
   - Version 10.0.22621.0 or higher
   - Included with Visual Studio UWP workload

5. **PowerShell 7.4+**
   - Download: [PowerShell 7](https://github.com/PowerShell/PowerShell)
   - Verify installation: `pwsh --version`

6. **Git for Windows**
   - Download: [Git](https://git-scm.com/download/win)
   - Configure Git:
     ```bash
     git config --global user.name "Your Name"
     git config --global user.email "your.email@example.com"
     ```

### Recommended Software

- **Windows Terminal** - Modern terminal experience
- **Visual Studio Code** - For markdown/JSON editing
- **GitHub Desktop** - GUI for Git (optional)
- **Process Monitor** - For debugging (Sysinternals)

---

## Environment Setup

### Step 1: Clone the Repository

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Better11.git
cd Better11

# Add upstream remote
git remote add upstream https://github.com/Cornman92/Better11.git

# Verify remotes
git remote -v
```

### Step 2: Install Visual Studio Workloads

1. Open Visual Studio Installer
2. Click "Modify" on Visual Studio 2022
3. Select workloads:
   - ✅ .NET Desktop Development
   - ✅ Universal Windows Platform Development
4. Click "Modify" to install

### Step 3: Verify Installation

```bash
# Check .NET version
dotnet --version
# Expected: 8.0.x

# Check PowerShell version
pwsh --version
# Expected: 7.4.x or higher

# Check Git version
git --version
# Expected: 2.x.x
```

---

## Building Better11

### Option 1: Using Visual Studio

1. Open `Better11.sln` in Visual Studio 2022
2. Select "Debug" or "Release" configuration
3. Press `Ctrl+Shift+B` to build
4. Press `F5` to run with debugging

### Option 2: Using Command Line

```bash
# Navigate to repository root
cd Better11

# Restore NuGet packages
dotnet restore

# Build in Debug mode
dotnet build

# Build in Release mode
dotnet build --configuration Release

# Run the application (once implemented)
dotnet run --project src/Better11.App
```

### Understanding the Build

The build process:
1. Restores NuGet packages
2. Compiles C# code
3. Compiles XAML resources
4. Generates output in `bin/` directory

---

## Project Structure Overview

```
Better11/
├── docs/                    # Documentation
│   ├── user-guide/         # User documentation
│   ├── developer-guide/    # Developer documentation
│   └── api/                # API reference
├── src/                    # Source code (coming soon)
│   ├── Better11.App/       # Main WinUI3 application
│   ├── Better11.Core/      # Core business logic
│   ├── Better11.Services/  # Service implementations
│   └── ...
├── tests/                  # Test projects (coming soon)
│   ├── Better11.UnitTests/
│   └── ...
├── scripts/                # Build/deployment scripts
├── samples/                # Sample code and plugins
├── PROJECT_PLAN.md         # Project plan
├── ARCHITECTURE.md         # Technical architecture
├── FEATURES.md            # Feature specifications
├── ROADMAP.md             # Development roadmap
├── TECH_STACK.md          # Technology details
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md              # Project overview
```

---

## Running Tests

### Once Tests are Implemented

```bash
# Run all tests
dotnet test

# Run unit tests only
dotnet test tests/Better11.UnitTests

# Run with code coverage
dotnet test /p:CollectCoverage=true

# Run specific test
dotnet test --filter "FullyQualifiedName~ImageServiceTests"

# Run tests in Visual Studio
# Test Explorer > Run All (Ctrl+R, A)
```

---

## Understanding the Architecture

### Layer Overview

1. **Presentation Layer** (Better11.App)
   - WinUI3 views and ViewModels
   - MVVM pattern
   - User interface

2. **Service Layer** (Better11.Services)
   - Business logic
   - Application services
   - Orchestration

3. **Core Layer** (Better11.Core)
   - Domain models
   - Business entities
   - Interfaces

4. **Infrastructure Layer** (Better11.Infrastructure)
   - Logging
   - Configuration
   - Data access
   - Cross-cutting concerns

### Key Technologies

- **UI**: WinUI3 (Windows App SDK)
- **Pattern**: MVVM (CommunityToolkit.Mvvm)
- **Language**: C# 12
- **Framework**: .NET 8.0
- **Scripting**: PowerShell 7+
- **Database**: SQLite
- **Logging**: Serilog
- **DI**: Microsoft.Extensions.DependencyInjection

See [TECH_STACK.md](TECH_STACK.md) for complete details.

---

## Making Your First Contribution

### Step 1: Find an Issue

- Look for issues labeled `good first issue`
- Check issues labeled `help wanted`
- Or propose a new feature/fix

### Step 2: Create a Branch

```bash
# Update develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Step 3: Make Changes

- Follow coding standards (see [CONTRIBUTING.md](CONTRIBUTING.md))
- Write tests for new code
- Update documentation
- Test your changes

### Step 4: Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Step 5: Create Pull Request

1. Go to GitHub
2. Click "Compare & pull request"
3. Fill out PR template
4. Submit for review

---

## Development Workflow

### Daily Workflow

```bash
# 1. Start your day - sync with upstream
git checkout develop
git pull upstream develop

# 2. Create/switch to feature branch
git checkout -b feature/my-feature
# or
git checkout feature/my-feature

# 3. Make changes
# Edit files in Visual Studio or VS Code

# 4. Test changes
dotnet test

# 5. Commit changes
git add .
git commit -m "feat: Descriptive message"

# 6. Push to your fork
git push origin feature/my-feature

# 7. Create PR when ready
# Use GitHub web interface
```

### Code-Build-Test Cycle

1. **Write code** in Visual Studio
2. **Build** with Ctrl+Shift+B
3. **Run** with F5
4. **Test** your changes
5. **Fix** any issues
6. **Repeat** until complete

---

## Common Development Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement feature in appropriate layer
3. Write unit tests
4. Update documentation
5. Test thoroughly
6. Submit PR

### Fixing a Bug

1. Create bugfix branch: `git checkout -b bugfix/issue-number`
2. Write failing test that reproduces bug
3. Fix the bug
4. Verify test passes
5. Submit PR

### Updating Documentation

1. Edit markdown files
2. Preview in VS Code or GitHub
3. Commit changes
4. Submit PR

---

## Troubleshooting

### Build Fails with "SDK not found"

**Solution**: Install .NET 8.0 SDK
```bash
# Verify installation
dotnet --version
```

### WinUI3 Package Not Found

**Solution**: Install UWP workload in Visual Studio
1. Open Visual Studio Installer
2. Modify Visual Studio 2022
3. Select "Universal Windows Platform development"
4. Install

### Tests Not Running

**Solution**: Rebuild solution
```bash
dotnet clean
dotnet restore
dotnet build
dotnet test
```

### Git Push Fails

**Solution**: Check remote configuration
```bash
git remote -v
# Ensure your fork is listed as 'origin'
```

---

## Learning Resources

### Documentation

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Project vision and plan
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [FEATURES.md](FEATURES.md) - Feature specifications
- [ROADMAP.md](ROADMAP.md) - Development roadmap
- [TECH_STACK.md](TECH_STACK.md) - Technology details
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide

### External Resources

**WinUI3**
- [WinUI 3 Documentation](https://docs.microsoft.com/en-us/windows/apps/winui/winui3/)
- [Windows App SDK](https://docs.microsoft.com/en-us/windows/apps/windows-app-sdk/)

**MVVM Toolkit**
- [MVVM Toolkit Documentation](https://docs.microsoft.com/en-us/windows/communitytoolkit/mvvm/introduction)

**.NET**
- [.NET Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [C# Documentation](https://docs.microsoft.com/en-us/dotnet/csharp/)

**PowerShell**
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)

---

## Getting Help

### Where to Ask

1. **Documentation**: Check docs first
2. **Issues**: Search existing issues
3. **Discussions**: Ask in GitHub Discussions
4. **Maintainers**: Reach out if needed

### How to Ask

- Be specific about your problem
- Include error messages
- Describe what you've tried
- Provide relevant code/configuration

---

## Next Steps

After completing this guide:

1. ✅ Explore the codebase (once implemented)
2. ✅ Read the architecture documentation
3. ✅ Try building and running the app
4. ✅ Look for `good first issue` labels
5. ✅ Join the community discussions
6. ✅ Make your first contribution!

---

## Quick Reference

### Essential Commands

```bash
# Clone
git clone https://github.com/YOUR-USERNAME/Better11.git

# Build
dotnet build

# Run
dotnet run --project src/Better11.App

# Test
dotnet test

# Create branch
git checkout -b feature/name

# Commit
git commit -m "type: message"

# Push
git push origin branch-name
```

### Keyboard Shortcuts (Visual Studio)

- `Ctrl+Shift+B` - Build solution
- `F5` - Start debugging
- `Ctrl+F5` - Start without debugging
- `Ctrl+R, A` - Run all tests
- `Ctrl+K, D` - Format document
- `Ctrl+.` - Quick actions

---

**Welcome to Better11 development!** 🚀

If you have questions, don't hesitate to ask in GitHub Discussions.

---

**Last Updated**: 2025-12-10
