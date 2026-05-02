using Orchestrator.Models;

namespace Orchestrator.Services;

public interface IWorkerService
{
    Task<IReadOnlyList<double>> PredictAsync(IReadOnlyList<double> features);
    Task ReloadAsync();
}

public class WorkerService(HttpClient http) : IWorkerService
{
    public async Task<IReadOnlyList<double>> PredictAsync(IReadOnlyList<double> features)
    {
        var response = await http.PostAsJsonAsync("/predict", new PredictRequest(features));
        response.EnsureSuccessStatusCode();
        var body = await response.Content.ReadFromJsonAsync<PredictResponse>()
            ?? throw new InvalidOperationException("Empty response from worker");
        return body.Forecast;
    }

    public async Task ReloadAsync()
    {
        var response = await http.PostAsync("/reload", null);
        response.EnsureSuccessStatusCode();
    }
}
