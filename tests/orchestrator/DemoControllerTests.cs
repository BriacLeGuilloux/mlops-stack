using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using Orchestrator.Models;
using Orchestrator.Services;
using System.Net;
using System.Net.Http.Json;
using Xunit;

namespace Orchestrator.Tests;

public class DemoControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public DemoControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Start_ReturnsAcceptedWithJobId()
    {
        var openMeteo = new Mock<IOpenMeteoService>();
        openMeteo
            .Setup(s => s.FetchLast90DaysAsync())
            .ReturnsAsync(new List<(DateTime, double)> { (DateTime.Today, 20.0) });

        var blob = new Mock<IBlobService>();
        blob.Setup(s => s.UploadCsvAsync(It.IsAny<IReadOnlyList<(DateTime, double)>>()))
            .Returns(Task.CompletedTask);

        var k8s = new Mock<IK8sJobService>();
        k8s.Setup(s => s.CreateTrainerJobAsync()).ReturnsAsync("trainer-20240101120000");

        var client = _factory.WithWebHostBuilder(builder =>
            builder.ConfigureServices(services =>
            {
                services.AddSingleton(openMeteo.Object);
                services.AddSingleton(blob.Object);
                services.AddSingleton(k8s.Object);
            })).CreateClient();

        var response = await client.PostAsync("/api/demo/start", null);

        Assert.Equal(HttpStatusCode.Accepted, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<StartDemoResponse>();
        Assert.NotNull(body);
        Assert.Equal("trainer-20240101120000", body.JobId);
    }
}
