using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Utilities
{
    /// <summary>
    /// Provides retry logic for operations that may fail transiently.
    /// </summary>
    public static class RetryHelper
    {
        /// <summary>
        /// Default retry policy: 3 attempts with exponential backoff (1s, 2s, 4s).
        /// </summary>
        public static readonly RetryPolicy DefaultPolicy = new RetryPolicy
        {
            MaxAttempts = 3,
            InitialDelay = TimeSpan.FromSeconds(1),
            MaxDelay = TimeSpan.FromSeconds(30),
            BackoffMultiplier = 2.0
        };

        /// <summary>
        /// Aggressive retry policy: 5 attempts with longer delays.
        /// </summary>
        public static readonly RetryPolicy AggressivePolicy = new RetryPolicy
        {
            MaxAttempts = 5,
            InitialDelay = TimeSpan.FromSeconds(2),
            MaxDelay = TimeSpan.FromMinutes(1),
            BackoffMultiplier = 2.0
        };

        /// <summary>
        /// Executes an operation with retry logic.
        /// </summary>
        /// <typeparam name="T">Return type of the operation.</typeparam>
        /// <param name="operation">The operation to execute.</param>
        /// <param name="policy">Retry policy to use. If null, uses DefaultPolicy.</param>
        /// <param name="shouldRetry">Optional predicate to determine if an exception should trigger a retry.</param>
        /// <param name="onRetry">Optional callback invoked before each retry attempt.</param>
        /// <param name="cancellationToken">Cancellation token.</param>
        /// <param name="logger">Optional logger for retry attempts.</param>
        /// <returns>The result of the operation.</returns>
        public static async Task<T> ExecuteWithRetryAsync<T>(
            Func<Task<T>> operation,
            RetryPolicy? policy = null,
            Func<Exception, bool>? shouldRetry = null,
            Action<int, Exception, TimeSpan>? onRetry = null,
            CancellationToken cancellationToken = default,
            ILogger? logger = null)
        {
            policy ??= DefaultPolicy;
            shouldRetry ??= DefaultShouldRetry;

            var attempt = 0;
            var currentDelay = policy.InitialDelay;

            while (true)
            {
                attempt++;

                try
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    return await operation();
                }
                catch (Exception ex) when (attempt < policy.MaxAttempts && shouldRetry(ex))
                {
                    logger?.LogWarning(ex,
                        "Operation failed (attempt {Attempt}/{MaxAttempts}). Retrying in {Delay}ms",
                        attempt, policy.MaxAttempts, currentDelay.TotalMilliseconds);

                    onRetry?.Invoke(attempt, ex, currentDelay);

                    await Task.Delay(currentDelay, cancellationToken);

                    // Calculate next delay with exponential backoff
                    currentDelay = TimeSpan.FromMilliseconds(
                        Math.Min(
                            currentDelay.TotalMilliseconds * policy.BackoffMultiplier,
                            policy.MaxDelay.TotalMilliseconds));
                }
                catch (Exception ex)
                {
                    // Either max attempts reached or exception shouldn't be retried
                    if (attempt >= policy.MaxAttempts)
                    {
                        logger?.LogError(ex,
                            "Operation failed after {Attempts} attempts",
                            attempt);
                    }
                    throw;
                }
            }
        }

        /// <summary>
        /// Executes an operation with retry logic (void return).
        /// </summary>
        public static async Task ExecuteWithRetryAsync(
            Func<Task> operation,
            RetryPolicy? policy = null,
            Func<Exception, bool>? shouldRetry = null,
            Action<int, Exception, TimeSpan>? onRetry = null,
            CancellationToken cancellationToken = default,
            ILogger? logger = null)
        {
            await ExecuteWithRetryAsync(
                async () =>
                {
                    await operation();
                    return true;
                },
                policy,
                shouldRetry,
                onRetry,
                cancellationToken,
                logger);
        }

        /// <summary>
        /// Default logic to determine if an exception should trigger a retry.
        /// Retries on network-related exceptions but not on validation errors.
        /// </summary>
        private static bool DefaultShouldRetry(Exception ex)
        {
            // Don't retry on cancellation
            if (ex is OperationCanceledException)
            {
                return false;
            }

            // Don't retry on argument/validation errors
            if (ex is ArgumentException or ArgumentNullException or InvalidOperationException)
            {
                return false;
            }

            // Retry on network-related exceptions
            if (ex is HttpRequestException or TimeoutException or System.Net.WebException)
            {
                return true;
            }

            // Retry on IO exceptions (might be transient file locks)
            if (ex is IOException)
            {
                return true;
            }

            // Don't retry by default for unknown exception types
            return false;
        }
    }

    /// <summary>
    /// Configuration for retry behavior.
    /// </summary>
    public class RetryPolicy
    {
        /// <summary>
        /// Maximum number of attempts (including the initial attempt).
        /// </summary>
        public int MaxAttempts { get; set; } = 3;

        /// <summary>
        /// Initial delay before the first retry.
        /// </summary>
        public TimeSpan InitialDelay { get; set; } = TimeSpan.FromSeconds(1);

        /// <summary>
        /// Maximum delay between retries.
        /// </summary>
        public TimeSpan MaxDelay { get; set; } = TimeSpan.FromSeconds(30);

        /// <summary>
        /// Multiplier for exponential backoff.
        /// Each retry delay is multiplied by this factor.
        /// </summary>
        public double BackoffMultiplier { get; set; } = 2.0;
    }
}
