using Microsoft.AspNetCore.Mvc;
using Orchestrator.Models;
using Orchestrator.Services;

namespace Orchestrator.Controllers;

[ApiController]
[Route("api/forecast")]
public class ForecastController(IWorkerService worker) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Get([FromQuery] double[]? features)
    {
        var input = features is { Length: > 0 }
            ? (IReadOnlyList<double>)features
            : Enumerable.Repeat(15.0, 30).ToArray();

        var forecast = await worker.PredictAsync(input);
        return Ok(new ForecastResponse(forecast));
    }
}
