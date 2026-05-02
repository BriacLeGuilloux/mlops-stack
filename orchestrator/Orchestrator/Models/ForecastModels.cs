namespace Orchestrator.Models;

public record StartDemoResponse(string JobId);

public record ForecastResponse(IReadOnlyList<double> Forecast);

public record StatusResponse(string Status);

public record PredictRequest(IReadOnlyList<double> Features);

public record PredictResponse(IReadOnlyList<double> Forecast);
