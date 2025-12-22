using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Result of a batch installation or uninstallation operation.
    /// </summary>
    public class BatchOperationResult
    {
        /// <summary>
        /// Individual results for each app in the batch.
        /// </summary>
        public List<BatchItemResult> Results { get; init; } = new();

        /// <summary>
        /// Total number of apps in the batch.
        /// </summary>
        public int TotalCount => Results.Count;

        /// <summary>
        /// Number of successful operations.
        /// </summary>
        public int SuccessCount => Results.Count(r => r.Success);

        /// <summary>
        /// Number of failed operations.
        /// </summary>
        public int FailureCount => Results.Count(r => !r.Success);

        /// <summary>
        /// Overall success (true if all operations succeeded).
        /// </summary>
        public bool AllSucceeded => Results.All(r => r.Success);

        /// <summary>
        /// Overall completion percentage.
        /// </summary>
        public double CompletionPercentage => TotalCount > 0
            ? (double)SuccessCount / TotalCount * 100
            : 0;

        /// <summary>
        /// Time when the batch operation started.
        /// </summary>
        public DateTime StartTime { get; init; } = DateTime.Now;

        /// <summary>
        /// Time when the batch operation completed.
        /// </summary>
        public DateTime? EndTime { get; set; }

        /// <summary>
        /// Total duration of the batch operation.
        /// </summary>
        public TimeSpan? Duration => EndTime.HasValue
            ? EndTime.Value - StartTime
            : null;
    }

    /// <summary>
    /// Result for a single item in a batch operation.
    /// </summary>
    public class BatchItemResult
    {
        /// <summary>
        /// Application ID.
        /// </summary>
        public required string AppId { get; init; }

        /// <summary>
        /// Whether the operation succeeded.
        /// </summary>
        public bool Success { get; init; }

        /// <summary>
        /// Error message if operation failed.
        /// </summary>
        public string? ErrorMessage { get; init; }

        /// <summary>
        /// Installed version (for install operations).
        /// </summary>
        public string? Version { get; init; }

        /// <summary>
        /// Operation status message.
        /// </summary>
        public string Status { get; init; } = string.Empty;

        /// <summary>
        /// Time when this item was processed.
        /// </summary>
        public DateTime ProcessedAt { get; init; } = DateTime.Now;

        /// <summary>
        /// Duration of this specific operation.
        /// </summary>
        public TimeSpan? Duration { get; init; }
    }
}
