using Microsoft.AspNetCore.Mvc;
using Orchestrator.Models;
using Orchestrator.Services;

namespace Orchestrator.Controllers;

[ApiController]
[Route("api/demo")]
public class DemoController(
    IOpenMeteoService openMeteo,
    IBlobService blob,
    IK8sJobService k8sJob) : ControllerBase
{
    [HttpPost("start")]
    public async Task<IActionResult> Start()
    {
        var data = await openMeteo.FetchLast90DaysAsync();
        await blob.UploadCsvAsync(data);
        var jobId = await k8sJob.CreateTrainerJobAsync();
        return Accepted(new StartDemoResponse(jobId));
    }
}
