namespace Better11.Core.Exceptions;

/// <summary>
/// Base exception for all Better11 exceptions.
/// </summary>
public class Better11Exception : Exception
{
    /// <summary>
    /// Initializes a new instance of the <see cref="Better11Exception"/> class.
    /// </summary>
    public Better11Exception()
    {
    }

    /// <summary>
    /// Initializes a new instance of the <see cref="Better11Exception"/> class with a specified error message.
    /// </summary>
    /// <param name="message">The message that describes the error.</param>
    public Better11Exception(string message) : base(message)
    {
    }

    /// <summary>
    /// Initializes a new instance of the <see cref="Better11Exception"/> class with a specified error message
    /// and a reference to the inner exception that is the cause of this exception.
    /// </summary>
    /// <param name="message">The error message that explains the reason for the exception.</param>
    /// <param name="innerException">The exception that is the cause of the current exception.</param>
    public Better11Exception(string message, Exception innerException) : base(message, innerException)
    {
    }
}

/// <summary>
/// Exception thrown when an image operation fails.
/// </summary>
public class ImageException : Better11Exception
{
    public ImageException() { }
    public ImageException(string message) : base(message) { }
    public ImageException(string message, Exception innerException) : base(message, innerException) { }
}

/// <summary>
/// Exception thrown when an application operation fails.
/// </summary>
public class AppException : Better11Exception
{
    public AppException() { }
    public AppException(string message) : base(message) { }
    public AppException(string message, Exception innerException) : base(message, innerException) { }
}

/// <summary>
/// Exception thrown when a file operation fails.
/// </summary>
public class FileOperationException : Better11Exception
{
    public FileOperationException() { }
    public FileOperationException(string message) : base(message) { }
    public FileOperationException(string message, Exception innerException) : base(message, innerException) { }
}

/// <summary>
/// Exception thrown when a deployment operation fails.
/// </summary>
public class DeploymentException : Better11Exception
{
    public DeploymentException() { }
    public DeploymentException(string message) : base(message) { }
    public DeploymentException(string message, Exception innerException) : base(message, innerException) { }
}
