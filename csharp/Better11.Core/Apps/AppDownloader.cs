using System.Net;
using System.Net.Http;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps;

/// <summary>
/// Downloads vetted installers from HTTP(S) or local file URIs.
/// </summary>
public class AppDownloader
{
    private readonly string _downloadRoot;
    private readonly string _sourceRoot;

    public AppDownloader(string downloadRoot, string? sourceRoot = null)
    {
        _downloadRoot = downloadRoot;
        _sourceRoot = sourceRoot ?? Directory.GetCurrentDirectory();
        Directory.CreateDirectory(_downloadRoot);
    }

    public async Task<string> DownloadAsync(AppMetadata app, string? destination = null)
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

            using var client = new HttpClient();
            using var response = await client.GetAsync(uri);
            response.EnsureSuccessStatusCode();

            await using var fileStream = File.Create(destination);
            await response.Content.CopyToAsync(fileStream);

            return destination;
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

    private string DestinationFor(AppMetadata app)
    {
        var uri = new Uri(app.Uri, UriKind.RelativeOrAbsolute);
        var filename = Path.GetFileName(uri.LocalPath);
        if (string.IsNullOrEmpty(filename))
        {
            throw new DownloadException($"Unable to determine filename from {app.Uri}");
        }
        return Path.Combine(_downloadRoot, filename);
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
