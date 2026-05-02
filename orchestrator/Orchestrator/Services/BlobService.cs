using System.Text;
using Azure.Storage.Blobs;

namespace Orchestrator.Services;

public interface IBlobService
{
    Task UploadCsvAsync(IReadOnlyList<(DateTime Date, double Temperature)> rows);
}

public class BlobService(BlobServiceClient blobServiceClient, IConfiguration config) : IBlobService
{
    public async Task UploadCsvAsync(IReadOnlyList<(DateTime Date, double Temperature)> rows)
    {
        var container = config["BLOB_CONTAINER"]
            ?? throw new InvalidOperationException("BLOB_CONTAINER not configured");

        var containerClient = blobServiceClient.GetBlobContainerClient(container);
        await containerClient.CreateIfNotExistsAsync();

        var sb = new StringBuilder("date,temperature\n");
        foreach (var (date, temp) in rows)
            sb.AppendLine($"{date:yyyy-MM-dd},{temp:F2}");

        var bytes = Encoding.UTF8.GetBytes(sb.ToString());
        var blobClient = containerClient.GetBlobClient("raw/brussels.csv");
        await blobClient.UploadAsync(new BinaryData(bytes), overwrite: true);
    }
}
