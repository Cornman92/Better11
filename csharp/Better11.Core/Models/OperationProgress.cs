using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents progress information for a long-running operation.
    /// </summary>
    public class OperationProgress
    {
        /// <summary>
        /// Unique identifier for the operation.
        /// </summary>
        public string OperationId { get; init; } = string.Empty;

        /// <summary>
        /// Application ID being processed.
        /// </summary>
        public string AppId { get; init; } = string.Empty;

        /// <summary>
        /// Current stage of the operation.
        /// </summary>
        public OperationStage Stage { get; init; }

        /// <summary>
        /// Progress percentage (0-100).
        /// </summary>
        public double PercentComplete { get; init; }

        /// <summary>
        /// Human-readable status message.
        /// </summary>
        public string Message { get; init; } = string.Empty;

        /// <summary>
        /// Total bytes to download (for download operations).
        /// </summary>
        public long? TotalBytes { get; init; }

        /// <summary>
        /// Bytes downloaded so far (for download operations).
        /// </summary>
        public long? BytesDownloaded { get; init; }

        /// <summary>
        /// Indicates if the operation is complete.
        /// </summary>
        public bool IsComplete { get; init; }

        /// <summary>
        /// Error message if operation failed.
        /// </summary>
        public string? ErrorMessage { get; init; }
    }

    /// <summary>
    /// Stages of an installation operation.
    /// </summary>
    public enum OperationStage
    {
        /// <summary>
        /// Initializing the operation.
        /// </summary>
        Initializing,

        /// <summary>
        /// Resolving dependencies.
        /// </summary>
        ResolvingDependencies,

        /// <summary>
        /// Downloading installer.
        /// </summary>
        Downloading,

        /// <summary>
        /// Verifying downloaded file.
        /// </summary>
        Verifying,

        /// <summary>
        /// Installing application.
        /// </summary>
        Installing,

        /// <summary>
        /// Updating installation state.
        /// </summary>
        UpdatingState,

        /// <summary>
        /// Operation completed successfully.
        /// </summary>
        Completed,

        /// <summary>
        /// Operation failed with error.
        /// </summary>
        Failed,

        /// <summary>
        /// Uninstalling application.
        /// </summary>
        Uninstalling
    }
}
