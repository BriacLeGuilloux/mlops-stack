namespace Orchestrator.Services;

public interface IOpenMeteoService
{
    Task<IReadOnlyList<(DateTime Date, double Temperature)>> FetchLast90DaysAsync();
}

public class OpenMeteoService(HttpClient http) : IOpenMeteoService
{
    private const double Latitude = 50.85;
    private const double Longitude = 4.35;

    public async Task<IReadOnlyList<(DateTime Date, double Temperature)>> FetchLast90DaysAsync()
    {
        var end = DateTime.UtcNow.Date;
        var start = end.AddDays(-90);
        var url = $"v1/forecast?latitude={Latitude}&longitude={Longitude}"
                + $"&daily=temperature_2m_max&start_date={start:yyyy-MM-dd}&end_date={end:yyyy-MM-dd}"
                + "&timezone=Europe%2FBrussels";

        var response = await http.GetFromJsonAsync<OpenMeteoResponse>(url)
            ?? throw new InvalidOperationException("Empty response from Open-Meteo");

        return response.Daily.Time
            .Zip(response.Daily.Temperature2mMax, (d, t) => (DateTime.Parse(d), t))
            .ToList();
    }

    private record OpenMeteoResponse(DailyData Daily);
    private record DailyData(
        List<string> Time,
        [property: System.Text.Json.Serialization.JsonPropertyName("temperature_2m_max")]
        List<double> Temperature2mMax
    );
}
