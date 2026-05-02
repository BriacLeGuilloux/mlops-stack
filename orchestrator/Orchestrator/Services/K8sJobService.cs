using k8s;
using k8s.Models;

namespace Orchestrator.Services;

public interface IK8sJobService
{
    Task<string> CreateTrainerJobAsync();
    Task<string> GetJobStatusAsync(string jobId);
}

public class K8sJobService(IKubernetes kubernetes, IConfiguration config) : IK8sJobService
{
    private const string Namespace = "mlops";
    private const string TrainerImage = "briacleguillou/trainer:latest";

    public async Task<string> CreateTrainerJobAsync()
    {
        var jobId = $"trainer-{DateTime.UtcNow:yyyyMMddHHmmss}";
        var job = new V1Job
        {
            Metadata = new V1ObjectMeta { Name = jobId, NamespaceProperty = Namespace },
            Spec = new V1JobSpec
            {
                Template = new V1PodTemplateSpec
                {
                    Spec = new V1PodSpec
                    {
                        NodeSelector = new Dictionary<string, string> { ["pool"] = "training" },
                        RestartPolicy = "Never",
                        Containers =
                        [
                            new V1Container
                            {
                                Name = "trainer",
                                Image = TrainerImage,
                                EnvFrom =
                                [
                                    new V1EnvFromSource(secretRef: new V1SecretEnvSource("mlops-secrets"))
                                ]
                            }
                        ]
                    }
                }
            }
        };

        await kubernetes.BatchV1.CreateNamespacedJobAsync(job, Namespace);
        return jobId;
    }

    public async Task<string> GetJobStatusAsync(string jobId)
    {
        var job = await kubernetes.BatchV1.ReadNamespacedJobAsync(jobId, Namespace);
        if (job.Status.Succeeded > 0) return "Succeeded";
        if (job.Status.Failed > 0) return "Failed";
        return "Running";
    }
}
