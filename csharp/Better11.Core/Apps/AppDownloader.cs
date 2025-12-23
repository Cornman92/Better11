using System.Net;
using System.Net.Http;
using Better11.Core.Apps.Models;
using Better11.Core.Models;
using Better11.Core.Utilities;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Apps;

/// <summary>
/// Downloads vetted installers from HTTP(S) or local file URIs.
/// </summary>
public class AppDownloader
{
    private readonly string _downloadRoot;
    private readonly string _sourceRoot;
    private readonly ILogger? _logger;

    public AppDownloader(string downloadRoot, string? sourceRoot = null, ILogger? logger = null)
    {
        _downloadRoot = downloadRoot;
        _sourceRoot = sourceRoot ?? Directory.GetCurrentDirectory();
        _logger = logger;
        Directory.CreateDirectory(_downloadRoot);
    }

    public async Task<string> DownloadAsync(
        AppMetadata app,
        string? destination = null,
        IProgress<OperationProgress>? progress = null,
        CancellationToken cancellationToken = default)
    {
        var uri = new Uri(app.Uri, UriKind.RelativeOrAbsolute);
        destination ??= DestinationFor(app);

        if (uri.Scheme == "http" || uri.Scheme == "https")
        {
            var hostname = uri.Host;
            if (!app.DomainIsVetted(hostname))
            {
                throw new DownloadException($"Host '{hostname}' is not in vetted domains for {app.AppId}");
            }

            // Wrap the download operation with retry logic
            return await RetryHelper.ExecuteWithRetryAsync(
                async () =>
                {
                    using var client = new HttpClient();
                    client.Timeout = TimeSpan.FromMinutes(30); // Allow for large downloads

                    // Get content length for progress reporting
                    using var headResponse = await client.SendAsync(new HttpRequestMessage(HttpMethod.Head, uri), cancellationToken);
                    var totalBytes = headResponse.Content.Headers.ContentLength;

                    using var response = await client.GetAsync(uri, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
                    response.EnsureSuccessStatusCode();

                    await using var fileStream = File.Create(destination);
                    await using var downloadStream = await response.Content.ReadAsStreamAsync(cancellationToken);

                    var buffer = new byte[8192];
                    long bytesDownloaded = 0;
                    int bytesRead;

                    while ((bytesRead = await downloadStream.ReadAsync(buffer, 0, buffer.Length, cancellationToken)) > 0)
                    {
                        cancellationToken.ThrowIfCancellationRequested();

                        await fileStream.WriteAsync(buffer, 0, bytesRead, cancellationToken);
                        bytesDownloaded += bytesRead;

                        if (progress != null && totalBytes.HasValue && totalBytes > 0)
                        {
                            var percentComplete = (double)bytesDownloaded / totalBytes.Value * 100;
                            progress.Report(new OperationProgress
                            {
                                AppId = app.AppId,
                                Stage = OperationStage.Downloading,
                                PercentComplete = percentComplete,
                                Message = $"Downloading {app.Name}: {FormatBytes(bytesDownloaded)} / {FormatBytes(totalBytes.Value)}",
                                TotalBytes = totalBytes.Value,
                                BytesDownloaded = bytesDownloaded,
                                IsComplete = false
                            });
                        }
                    }

                    return destination;
                },
                policy: RetryHelper.DefaultPolicy,
                onRetry: (attempt, exception, delay) =>
                {
                    _logger?.LogWarning("Download retry attempt {Attempt} for {AppName} after {Delay}ms due to: {Error}",
                        attempt, app.Name, delay.TotalMilliseconds, exception.Message);

                    progress?.Report(new OperationProgress
                    {
                        AppId = app.AppId,
                        Stage = OperationStage.Downloading,
                        PercentComplete = 0,
                        Message = $"Retrying download (attempt {attempt + 1})...",
                        IsComplete = false
                    });
                },
                cancellationToken: cancellationToken,
                logger: _logger);
        }

        if (uri.Scheme == "file" || uri.Scheme == "")
        {
            var source = uri.IsAbsoluteUri ? uri.LocalPath : Path.Combine(_sourceRoot, uri.OriginalString);
            if (!Path.IsPathRooted(source))
            {
                source = Path.Combine(_sourceRoot, source);
            }
            source = Path.GetFullPath(source);

            if (!File.Exists(source))
            {
                throw new DownloadException($"Local source does not exist: {source}");
            }

            File.Copy(source, destination, overwrite: true);
            return destination;
        }

        throw new DownloadException($"Unsupported URI scheme for {app.Uri}");
    }

    public string DestinationFor(AppMetadata app)
    {
        var uri = new Uri(app.Uri, UriKind.RelativeOrAbsolute);
        var filename = Path.GetFileName(uri.LocalPath);
        if (string.IsNullOrEmpty(filename))
        {
            throw new DownloadException($"Unable to determine filename from {app.Uri}");
        }
        return Path.Combine(_downloadRoot, filename);
    }

    private static string FormatBytes(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len /= 1024;
        }
        return $"{len:0.##} {sizes[order]}";
    }
}

/// <summary>
/// Exception thrown when download fails.
/// </summary>
public class DownloadException : Exception
{
    public DownloadException(string message) : base(message) { }
    public DownloadException(string message, Exception innerException) : base(message, innerException) { }
}
