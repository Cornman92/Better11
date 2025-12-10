# Contributing to Better11

Thank you for your interest in contributing to Better11! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behavior includes**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes**:
- Harassment, trolling, or derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- Windows 11 (Build 22621 or higher)
- Visual Studio 2022 (v17.8 or higher)
- .NET 8.0 SDK
- PowerShell 7.4+
- Git for Windows

### First-Time Contributors

1. **Find an issue**: Look for issues labeled `good first issue` or `help wanted`
2. **Ask questions**: Don't hesitate to ask for clarification on issues
3. **Start small**: Begin with documentation or small bug fixes
4. **Learn the codebase**: Review the architecture and existing code

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/Better11.git
cd Better11

# Add upstream remote
git remote add upstream https://github.com/Cornman92/Better11.git
```

### 2. Install Visual Studio Workloads

Required workloads:
- .NET Desktop Development
- Universal Windows Platform Development

### 3. Install Required SDKs

- Windows 11 SDK (10.0.22621.0)
- .NET 8.0 SDK

### 4. Restore Dependencies

```bash
# Restore NuGet packages
dotnet restore

# Or open the solution in Visual Studio and it will restore automatically
```

### 5. Build the Solution

```bash
# Build in Debug mode
dotnet build

# Or use Visual Studio Build > Build Solution (Ctrl+Shift+B)
```

### 6. Run the Application

```bash
# Run from command line
dotnet run --project src/Better11.App

# Or press F5 in Visual Studio
```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical bug fixes for production

### Creating a Feature Branch

```bash
# Update your local develop branch
git checkout develop
git pull upstream develop

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "Add: Your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

Follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(image-editor): Add driver injection functionality

- Implement driver enumeration
- Add batch driver injection
- Include driver validation

Closes #123
```

```
fix(app-manager): Fix crash when searching with empty query

The search function was not handling empty queries properly,
causing a NullReferenceException.

Fixes #456
```

---

## Coding Standards

### C# Style Guide

Follow the [Microsoft C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions).

#### Naming Conventions

```csharp
// PascalCase for public members
public class ImageService { }
public void LoadImage() { }
public string ImagePath { get; set; }

// camelCase for private fields with underscore prefix
private readonly ILogger _logger;
private string _imagePath;

// PascalCase for constants
public const int MaxImageSize = 1024;

// Interface names start with 'I'
public interface IImageService { }

// Async methods end with 'Async'
public async Task LoadImageAsync() { }
```

#### File Organization

```csharp
// File-scoped namespace (C# 10+)
namespace Better11.Services;

// Using directives at top
using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

// Class structure order:
// 1. Constants
// 2. Static fields
// 3. Fields
// 4. Constructors
// 5. Properties
// 6. Public methods
// 7. Private methods

public class ImageService : IImageService
{
    // Constants
    private const int DefaultTimeout = 30000;

    // Fields
    private readonly ILogger<ImageService> _logger;
    private readonly IWimManager _wimManager;

    // Constructor
    public ImageService(ILogger<ImageService> logger, IWimManager wimManager)
    {
        _logger = logger;
        _wimManager = wimManager;
    }

    // Properties
    public bool IsImageLoaded { get; private set; }

    // Public methods
    public async Task<WindowsImage> LoadImageAsync(string path)
    {
        _logger.LogInformation("Loading image from {Path}", path);
        return await LoadImageInternalAsync(path);
    }

    // Private methods
    private async Task<WindowsImage> LoadImageInternalAsync(string path)
    {
        // Implementation
    }
}
```

### XAML Style Guide

```xaml
<!-- Use consistent indentation (4 spaces) -->
<!-- Order attributes: x:Name, x:Key, common properties, attached properties, event handlers -->
<Button x:Name="LoadButton"
        Content="Load Image"
        HorizontalAlignment="Stretch"
        Margin="0,8,0,0"
        Grid.Row="1"
        Click="LoadButton_Click" />

<!-- Use meaningful names -->
<ListView x:Name="DriverListView" />

<!-- Group related properties -->
<StackPanel Orientation="Vertical"
            Spacing="8"
            Padding="16">
    <!-- Content -->
</StackPanel>
```

### Code Quality

- **Enable nullable reference types**: All projects use `<Nullable>enable</Nullable>`
- **Use async/await**: For I/O and long-running operations
- **Handle exceptions**: Use try-catch appropriately, log errors
- **Dispose resources**: Implement IDisposable when needed
- **Avoid code smells**: No magic numbers, long methods, or deep nesting

#### Example: Proper Error Handling

```csharp
public async Task<Result<WindowsImage>> LoadImageAsync(string path, CancellationToken ct = default)
{
    try
    {
        _logger.LogInformation("Loading image from {Path}", path);

        if (string.IsNullOrWhiteSpace(path))
            return Result<WindowsImage>.Failure("Image path cannot be empty");

        if (!File.Exists(path))
            return Result<WindowsImage>.Failure("Image file not found");

        var image = await _wimManager.LoadImageAsync(path, ct);
        return Result<WindowsImage>.Success(image);
    }
    catch (OperationCanceledException)
    {
        _logger.LogInformation("Image loading cancelled");
        throw;
    }
    catch (ImageException ex)
    {
        _logger.LogError(ex, "Failed to load image from {Path}", path);
        return Result<WindowsImage>.Failure(ex.Message);
    }
    catch (Exception ex)
    {
        _logger.LogCritical(ex, "Unexpected error loading image from {Path}", path);
        return Result<WindowsImage>.Failure("An unexpected error occurred");
    }
}
```

---

## Testing

### Unit Tests

- Write unit tests for all business logic
- Use xUnit for test framework
- Use Moq for mocking
- Aim for >80% code coverage

```csharp
public class ImageServiceTests
{
    private readonly Mock<ILogger<ImageService>> _mockLogger;
    private readonly Mock<IWimManager> _mockWimManager;
    private readonly ImageService _sut; // System Under Test

    public ImageServiceTests()
    {
        _mockLogger = new Mock<ILogger<ImageService>>();
        _mockWimManager = new Mock<IWimManager>();
        _sut = new ImageService(_mockLogger.Object, _mockWimManager.Object);
    }

    [Fact]
    public async Task LoadImageAsync_ValidPath_ReturnsSuccess()
    {
        // Arrange
        var path = "test.wim";
        var expectedImage = new WindowsImage();
        _mockWimManager
            .Setup(x => x.LoadImageAsync(path, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedImage);

        // Act
        var result = await _sut.LoadImageAsync(path);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.Should().Be(expectedImage);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("   ")]
    public async Task LoadImageAsync_InvalidPath_ReturnsFailure(string path)
    {
        // Act
        var result = await _sut.LoadImageAsync(path);

        // Assert
        result.IsSuccess.Should().BeFalse();
        result.Error.Should().Contain("cannot be empty");
    }
}
```

### Running Tests

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# Run specific test
dotnet test --filter "FullyQualifiedName~ImageServiceTests"
```

### Integration Tests

- Test integration between components
- Use actual dependencies where possible
- Mock external systems (network, file system when appropriate)

### UI Tests

- Test critical user workflows
- Use WinAppDriver for automation
- Keep tests maintainable and reliable

---

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Unit tests added/updated
- [ ] All tests pass locally
- [ ] Build succeeds without errors

### Submitting a Pull Request

1. **Update your branch**:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout feature/your-feature
   git rebase develop
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature
   ```

3. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Target the `develop` branch
   - Fill out the PR template
   - Link related issues

4. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Related Issues
   Closes #123

   ## Testing
   Describe testing performed

   ## Screenshots (if applicable)
   Add screenshots here

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Tests added/updated
   - [ ] Documentation updated
   ```

### Code Review Process

1. **Automated checks**: CI/CD pipeline must pass
2. **Peer review**: At least one approval required
3. **Address feedback**: Respond to all comments
4. **Final approval**: Maintainer approval required
5. **Merge**: Maintainer will merge when ready

---

## Issue Guidelines

### Reporting Bugs

Use the bug report template and include:
- Better11 version
- Windows version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/logs if applicable

**Example**:
```markdown
**Better11 Version**: 1.0.0
**Windows Version**: Windows 11 22H2 (Build 22621.1234)

**Steps to Reproduce**:
1. Open Image Editor
2. Select a WIM file
3. Click "Mount Image"
4. Application crashes

**Expected**: Image should mount successfully
**Actual**: Application crashes with error: "Access Denied"

**Logs**:
```
2025-12-10 10:30:15 [ERROR] Failed to mount image: Access is denied
```

### Suggesting Features

Use the feature request template and include:
- Problem/need description
- Proposed solution
- Alternatives considered
- Additional context

### Asking Questions

- Check existing issues first
- Use Discussions for general questions
- Be specific and provide context

---

## Documentation

### Code Documentation

- Use XML documentation comments for public APIs
- Document complex algorithms
- Include usage examples

```csharp
/// <summary>
/// Loads a Windows image from the specified path.
/// </summary>
/// <param name="path">The full path to the WIM file.</param>
/// <param name="ct">Cancellation token to cancel the operation.</param>
/// <returns>
/// A <see cref="Result{T}"/> containing the loaded <see cref="WindowsImage"/> on success,
/// or an error message on failure.
/// </returns>
/// <exception cref="OperationCanceledException">Thrown when the operation is cancelled.</exception>
/// <example>
/// <code>
/// var result = await imageService.LoadImageAsync("C:\\install.wim");
/// if (result.IsSuccess)
/// {
///     var image = result.Value;
///     // Use the image
/// }
/// </code>
/// </example>
public async Task<Result<WindowsImage>> LoadImageAsync(string path, CancellationToken ct = default)
```

### User Documentation

- Update user guide for new features
- Include screenshots
- Provide step-by-step instructions
- Keep documentation up-to-date

### API Documentation

- Generate API docs with DocFX or similar
- Include code examples
- Document breaking changes

---

## Project Structure

```
Better11/
├── .github/              # GitHub workflows, issue templates
├── docs/                 # Documentation
├── samples/              # Sample code and plugins
├── scripts/              # Build and utility scripts
├── src/                  # Source code
│   ├── Better11.App/
│   ├── Better11.Core/
│   ├── Better11.Services/
│   ├── Better11.Infrastructure/
│   └── Better11.PowerShell/
├── tests/                # Test projects
│   ├── Better11.UnitTests/
│   ├── Better11.IntegrationTests/
│   └── Better11.E2ETests/
├── tools/                # Development tools
├── .editorconfig         # Editor configuration
├── .gitignore
├── Better11.sln          # Solution file
├── LICENSE
├── README.md
└── CONTRIBUTING.md       # This file
```

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, general discussion
- **Pull Requests**: Code contributions

### Getting Help

- Check documentation first
- Search existing issues
- Ask in Discussions
- Be patient and respectful

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in the project

---

## Development Tips

### Visual Studio Extensions

Recommended extensions:
- **XAML Styler**: Automatic XAML formatting
- **CodeMaid**: Code cleanup and organization
- **SonarLint**: Code quality analysis
- **Roslynator**: Additional analyzers and refactorings

### Debugging

- Use breakpoints and step-through debugging
- Enable Exception Settings for better error catching
- Use Diagnostic Tools for performance profiling
- Check Output window for XAML binding errors

### Performance

- Profile before optimizing
- Use async/await properly
- Avoid UI thread blocking
- Dispose resources promptly

### Common Pitfalls

- **Not handling null**: Use nullable reference types
- **Blocking UI thread**: Use async operations
- **Memory leaks**: Unsubscribe from events, dispose resources
- **Magic numbers**: Use named constants
- **Tight coupling**: Use interfaces and DI

---

## License

By contributing to Better11, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

## Questions?

If you have questions about contributing, please:
1. Check this guide thoroughly
2. Review existing issues and discussions
3. Ask in GitHub Discussions
4. Reach out to maintainers

Thank you for contributing to Better11! 🚀

---

**Document Version**: 1.0
**Last Updated**: 2025-12-10
