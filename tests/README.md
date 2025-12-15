# Better11 Tests

This directory contains all test projects for Better11.

## Test Projects

### Better11.UnitTests
Unit tests for individual components and classes.

**Framework**: xUnit
**Coverage Target**: >80%

**Structure**:
```
Better11.UnitTests/
├── Services/
│   ├── ImageServiceTests.cs
│   ├── AppServiceTests.cs
│   └── FileServiceTests.cs
├── ViewModels/
│   ├── DashboardViewModelTests.cs
│   └── ImageEditorViewModelTests.cs
└── Core/
    └── ModelsTests.cs
```

### Better11.IntegrationTests
Integration tests for component interactions and workflows.

**Framework**: xUnit/MSTest
**Focus**: Service integration, data access, external system interaction

**Structure**:
```
Better11.IntegrationTests/
├── Services/
│   ├── ImageWorkflowTests.cs
│   └── AppInstallationTests.cs
└── Infrastructure/
    └── DataAccessTests.cs
```

### Better11.E2ETests
End-to-end tests for complete user workflows.

**Framework**: WinAppDriver + xUnit
**Focus**: UI automation, user scenarios

**Structure**:
```
Better11.E2ETests/
├── ImageEditorTests.cs
├── AppManagerTests.cs
└── FileOperationsTests.cs
```

## Running Tests

### All Tests
```bash
dotnet test
```

### Specific Test Project
```bash
dotnet test tests/Better11.UnitTests
```

### With Coverage
```bash
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
```

### Specific Test
```bash
dotnet test --filter "FullyQualifiedName~ImageServiceTests.LoadImage_ValidPath"
```

### By Category
```bash
dotnet test --filter "Category=Unit"
```

## Test Organization

### Naming Convention
```csharp
[MethodName]_[Scenario]_[ExpectedResult]
```

**Examples**:
- `LoadImage_ValidPath_ReturnsSuccess`
- `InstallApp_InvalidPackage_ReturnsFailure`
- `SearchFiles_EmptyQuery_ThrowsArgumentException`

### Test Structure (AAA Pattern)
```csharp
[Fact]
public async Task LoadImage_ValidPath_ReturnsSuccess()
{
    // Arrange
    var path = "test.wim";
    var mockWimManager = new Mock<IWimManager>();
    var service = new ImageService(mockWimManager.Object);

    // Act
    var result = await service.LoadImageAsync(path);

    // Assert
    Assert.True(result.IsSuccess);
    Assert.NotNull(result.Value);
}
```

## Test Categories

Use categories to organize tests:
```csharp
[Trait("Category", "Unit")]
[Trait("Category", "Integration")]
[Trait("Category", "E2E")]
[Trait("Category", "Slow")]
```

## Mocking

**Library**: Moq

**Example**:
```csharp
var mockService = new Mock<IImageService>();
mockService
    .Setup(x => x.LoadImageAsync(It.IsAny<string>()))
    .ReturnsAsync(new WindowsImage());
```

## Test Data

Store test data in:
```
tests/TestData/
├── Images/
│   └── test.wim
├── Configs/
│   └── test-config.json
└── Scripts/
    └── test-script.ps1
```

## Code Coverage

### Viewing Coverage
```bash
# Generate coverage report
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# Generate HTML report (requires ReportGenerator)
reportgenerator -reports:coverage.opencover.xml -targetdir:coverage-report
```

### Coverage Goals
- Overall: >80%
- Business Logic: >90%
- ViewModels: >85%
- Infrastructure: >70%

## Continuous Integration

Tests run automatically on:
- Every push to develop/main
- Every pull request
- Nightly builds

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Fast Tests**: Unit tests should complete in milliseconds
3. **Readable Tests**: Tests should be self-documenting
4. **Maintainable**: Avoid test duplication, use helpers
5. **Deterministic**: Tests should always produce the same result
6. **No External Dependencies**: Mock external systems
7. **Clean Up**: Dispose resources properly

## Common Testing Patterns

### Testing Async Methods
```csharp
[Fact]
public async Task AsyncMethod_Scenario_Result()
{
    var result = await service.MethodAsync();
    Assert.NotNull(result);
}
```

### Testing Exceptions
```csharp
[Fact]
public async Task Method_InvalidInput_ThrowsException()
{
    await Assert.ThrowsAsync<ArgumentException>(
        () => service.MethodAsync(null));
}
```

### Testing with FluentAssertions
```csharp
[Fact]
public void Method_Scenario_Result()
{
    var result = service.Method();

    result.Should().NotBeNull();
    result.Value.Should().Be(42);
    result.Items.Should().HaveCount(3);
}
```

## Troubleshooting

### Tests Not Discovered
- Rebuild the solution
- Check test project targets .NET 8.0
- Ensure xUnit runner is installed

### Tests Timeout
- Increase test timeout
- Check for deadlocks
- Use cancellation tokens properly

### Flaky Tests
- Identify timing issues
- Remove dependencies on external state
- Use deterministic data

---

**Status**: Planning Phase - Tests coming soon!
**Last Updated**: 2025-12-10
