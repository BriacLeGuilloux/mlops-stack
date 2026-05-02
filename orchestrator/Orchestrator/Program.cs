using Azure.Storage.Blobs;
using k8s;
using Orchestrator.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddSingleton(_ =>
    new BlobServiceClient(builder.Configuration["AZURE_STORAGE_CONN_STR"]
        ?? throw new InvalidOperationException("AZURE_STORAGE_CONN_STR not configured")));

builder.Services.AddSingleton<IKubernetes>(_ =>
{
    var kubeconfigPath = builder.Configuration["KUBECONFIG"] ?? KubernetesClientConfiguration.KubeConfigDefaultLocation;
    var config = KubernetesClientConfiguration.BuildConfigFromConfigFile(kubeconfigPath);
    return new Kubernetes(config);
});

builder.Services.AddHttpClient<IOpenMeteoService, OpenMeteoService>(client =>
{
    var baseUrl = builder.Configuration["OPENMETEO_BASE_URL"] ?? "https://api.open-meteo.com";
    client.BaseAddress = new Uri(baseUrl);
});

builder.Services.AddHttpClient<IWorkerService, WorkerService>(client =>
{
    var workerUrl = builder.Configuration["WORKER_URL"]
        ?? throw new InvalidOperationException("WORKER_URL not configured");
    client.BaseAddress = new Uri(workerUrl);
});

builder.Services.AddScoped<IBlobService, BlobService>();
builder.Services.AddScoped<IK8sJobService, K8sJobService>();

var app = builder.Build();

app.MapControllers();
app.Run();

public partial class Program { }
