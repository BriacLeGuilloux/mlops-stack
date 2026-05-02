using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using Orchestrator.Models;
using Orchestrator.Services;
using System.Net;
using System.Net.Http.Json;
using Xunit;

namespace Orchestrator.Tests;

public class StatusControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public StatusControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Get_WhenSucceeded_ReloadsWorkerAndReturnsStatus()
    {
        var k8s = new Mock<IK8sJobService>();
        k8s.Setup(s => s.GetJobStatusAsync("job-1")).ReturnsAsync("Succeeded");

        var worker = new Mock<IWorkerService>();
        worker.Setup(s => s.ReloadAsync()).Returns(Task.CompletedTask);

        var client = _factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                services.AddSingleton(k8s.Object);
                services.AddSingleton(worker.Object);
            })).CreateClient();

        var response = await client.GetAsync("/api/status/job-1");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<StatusResponse>();
        Assert.Equal("Succeeded", body!.Status);
        worker.Verify(s => s.ReloadAsync(), Times.Once);
    }

    [Fact]
    public async Task Get_WhenRunning_DoesNotReloadWorker()
    {
        var k8s = new Mock<IK8sJobService>();
        k8s.Setup(s => s.GetJobStatusAsync("job-2")).ReturnsAsync("Running");

        var worker = new Mock<IWorkerService>();

        var client = _factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                services.AddSingleton(k8s.Object);
                services.AddSingleton(worker.Object);
            })).CreateClient();

        var response = await client.GetAsync("/api/status/job-2");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        worker.Verify(s => s.ReloadAsync(), Times.Never);
    }
}
