using Better11.Core.Models;
using FluentAssertions;
using Xunit;

namespace Better11.UnitTests.Core;

/// <summary>
/// Unit tests for the Result<T> class.
/// </summary>
public class ResultTests
{
    [Fact]
    public void Success_WithValue_ReturnsSuccessfulResult()
    {
        // Arrange
        var expectedValue = "test value";

        // Act
        var result = Result<string>.Success(expectedValue);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.IsFailure.Should().BeFalse();
        result.Value.Should().Be(expectedValue);
        result.Error.Should().BeNull();
    }

    [Fact]
    public void Failure_WithError_ReturnsFailedResult()
    {
        // Arrange
        var expectedError = "test error";

        // Act
        var result = Result<string>.Failure(expectedError);

        // Assert
        result.IsSuccess.Should().BeFalse();
        result.IsFailure.Should().BeTrue();
        result.Value.Should().BeNull();
        result.Error.Should().Be(expectedError);
    }

    [Fact]
    public void Match_WhenSuccess_ExecutesSuccessFunction()
    {
        // Arrange
        var result = Result<int>.Success(42);
        var successCalled = false;
        var failureCalled = false;

        // Act
        var output = result.Match(
            onSuccess: value =>
            {
                successCalled = true;
                return $"Success: {value}";
            },
            onFailure: error =>
            {
                failureCalled = true;
                return $"Failure: {error}";
            });

        // Assert
        successCalled.Should().BeTrue();
        failureCalled.Should().BeFalse();
        output.Should().Be("Success: 42");
    }

    [Fact]
    public void Match_WhenFailure_ExecutesFailureFunction()
    {
        // Arrange
        var result = Result<int>.Failure("error message");
        var successCalled = false;
        var failureCalled = false;

        // Act
        var output = result.Match(
            onSuccess: value =>
            {
                successCalled = true;
                return $"Success: {value}";
            },
            onFailure: error =>
            {
                failureCalled = true;
                return $"Failure: {error}";
            });

        // Assert
        successCalled.Should().BeFalse();
        failureCalled.Should().BeTrue();
        output.Should().Be("Failure: error message");
    }
}

/// <summary>
/// Unit tests for the Result class (non-generic).
/// </summary>
public class ResultNonGenericTests
{
    [Fact]
    public void Success_ReturnsSuccessfulResult()
    {
        // Act
        var result = Result.Success();

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.IsFailure.Should().BeFalse();
        result.Error.Should().BeNull();
    }

    [Fact]
    public void Failure_WithError_ReturnsFailedResult()
    {
        // Arrange
        var expectedError = "test error";

        // Act
        var result = Result.Failure(expectedError);

        // Assert
        result.IsSuccess.Should().BeFalse();
        result.IsFailure.Should().BeTrue();
        result.Error.Should().Be(expectedError);
    }
}
