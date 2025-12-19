using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;
using System.Text;

namespace Better11.App.Services;

/// <summary>
/// Service for handling global application errors.
/// </summary>
public interface IErrorHandlingService
{
    /// <summary>
    /// Handle an unhandled exception.
    /// </summary>
    void HandleException(Exception exception, string context = "");

    /// <summary>
    /// Get error logs.
    /// </summary>
    string GetErrorLogs();

    /// <summary>
    /// Clear error logs.
    /// </summary>
    void ClearErrorLogs();
}

/// <summary>
/// Implementation of error handling service.
/// </summary>
public class ErrorHandlingService : IErrorHandlingService
{
    private readonly ILogger<ErrorHandlingService> _logger;
    private readonly StringBuilder _errorLog;
    private readonly object _lockObject = new();

    /// <summary>
    /// Initializes a new instance of the <see cref="ErrorHandlingService"/> class.
    /// </summary>
    public ErrorHandlingService(ILogger<ErrorHandlingService> logger)
    {
        _logger = logger;
        _errorLog = new StringBuilder();
    }

    /// <inheritdoc/>
    public void HandleException(Exception exception, string context = "")
    {
        lock (_lockObject)
        {
            var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            var contextInfo = string.IsNullOrEmpty(context) ? "" : $" [{context}]";

            var errorMessage = $"[{timestamp}]{contextInfo} {exception.GetType().Name}: {exception.Message}";

            _logger.LogError(exception, "Unhandled exception{Context}", contextInfo);

            _errorLog.AppendLine(errorMessage);
            _errorLog.AppendLine($"  Stack Trace: {exception.StackTrace}");

            if (exception.InnerException != null)
            {
                _errorLog.AppendLine($"  Inner Exception: {exception.InnerException.Message}");
                _errorLog.AppendLine($"  Inner Stack Trace: {exception.InnerException.StackTrace}");
            }

            _errorLog.AppendLine();
        }
    }

    /// <inheritdoc/>
    public string GetErrorLogs()
    {
        lock (_lockObject)
        {
            return _errorLog.ToString();
        }
    }

    /// <inheritdoc/>
    public void ClearErrorLogs()
    {
        lock (_lockObject)
        {
            _errorLog.Clear();
        }
    }
}
