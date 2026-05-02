using Microsoft.AspNetCore.Mvc;
using Orchestrator.Models;
using Orchestrator.Services;

namespace Orchestrator.Controllers;

[ApiController]
[Route("api/status")]
public class StatusController(IK8sJobService k8sJob, IWorkerService worker) : ControllerBase
{
    [HttpGet("{jobId}")]
    public async Task<IActionResult> Get(string jobId)
    {
        var status = await k8sJob.GetJobStatusAsync(jobId);
        if (status == "Succeeded")
            await worker.ReloadAsync();
        return Ok(new StatusResponse(status));
    }
}
