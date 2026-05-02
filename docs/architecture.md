# MLOps Stack — Architecture

Projet MLOps : prévision température Bruxelles 14j, LSTM PyTorch, déclenché depuis .NET 8.
Docker Hub: `briacleguillou` | Ordre de build: bottom-up

---

## Structure

```text
mlops-stack/
├── .docker/
│   ├── python-base.Dockerfile
│   ├── trainer.Dockerfile
│   ├── worker.Dockerfile
│   └── orchestrator.Dockerfile
├── python/
│   ├── trainer/
│   │   ├── model.py / train.py / requirements.txt
│   └── worker/
│       ├── main.py / requirements.txt
├── tests/
│   ├── trainer/
│   │   └── test_train.py
│   ├── worker/
│   │   └── test_main.py
│   └── orchestrator/
│       └── Orchestrator.Tests.csproj
├── orchestrator/
│   ├── Orchestrator/
│   │   ├── Controllers/           # Demo, Forecast, Status
│   │   ├── Services/              # OpenMeteo, Blob, K8sJob, Worker
│   │   ├── Models/                # record DTOs
│   │   └── Program.cs
│   └── orchestrator.sln
├── helm/mlops-stack/
│   ├── Chart.yaml / values.yaml / values-prod.yaml
│   └── templates/
│       ├── orchestrator-deployment.yaml
│       ├── worker-deployment.yaml
│       ├── trainer-job-template.yaml
│       ├── services.yaml
│       ├── configmap.yaml
│       └── secretproviderclass.yaml
├── terraform/
│   ├── main.tf / variables.tf / outputs.tf / backend.tf
│   ├── environments/ (dev.tfvars, prod.tfvars)
│   └── modules/ (aks, storage, networking, keyvault)
├── pipelines/
│   ├── ci.yml       # Azure DevOps — build + test + push
│   └── release.yml  # Azure DevOps — terraform + helm + smoke
└── README.md
```

---

## Composants

### Images Docker

| Image | Base | Rôle |
| --- | --- | --- |
| `python-base` | `python:3.14-slim` | pandas / numpy / scikit-learn / azure-storage-blob |
| `trainer` | `python-base` | Entraîne le LSTM, upload le `.pt` dans Azure Blob |
| `worker` | `python-base` | FastAPI : `/predict`, `/reload` |
| `orchestrator` | `aspnet:8.0` | .NET 8 Web API, point d'entrée unique |

### Trainer (`python/trainer/`)

- `model.py` : `LSTMModel(input=1, hidden=64, layers=2, output=14)`
- `train.py` : télécharge `raw/brussels.csv` → normalisation + fenêtres 30→14 → 50 epochs → upload `models/lstm_vN.pt`
- Env vars : `AZURE_STORAGE_CONN_STR`, `BLOB_CONTAINER`

### Worker (`python/worker/main.py`)

- Lifespan : télécharge le dernier `.pt` depuis Azure Blob
- `POST /predict` `{features: [float]}` → `{forecast: [14 floats]}`
- `POST /reload` → re-télécharge le modèle → 204

### Orchestrateur (.NET 8 — structure plate)

Services : `OpenMeteoService`, `BlobService`, `K8sJobService`, `WorkerService`

**Flow de démo :**

1. `POST /api/demo/start` → fetch 90j Open-Meteo → upload `raw/brussels.csv` → create K8s Job → `202 {jobId}`
2. `GET /api/status/{jobId}` → statut K8s ; si `Succeeded` → `WorkerService.ReloadAsync()` → `{status}`
3. `GET /api/forecast` → proxy `WorkerService.PredictAsync()`

### Infrastructure

- **AKS** : 2 node pools — `default` (always-on) + `training` (autoscale 0→1)
- **Azure Blob Storage** : containers `raw/`, `processed/`, `models/`, `tfstate`
- **Key Vault** : secrets montés via CSI driver dans les pods K8s
- **Helm** : déploiement orchestrateur + worker ; Job trainer en ConfigMap

### Pipelines Azure DevOps

**`ci.yml`** (push / PR → main) : ruff + pytest → dotnet test → docker build + push

**`release.yml`** (manuel, variable `environment`) : terraform apply → helm upgrade → smoke test

---

## Vérification

1. `docker run briacleguillou/trainer` → `models/lstm_v1.pt` présent dans le blob
2. `docker run -p 8000:8000 briacleguillou/worker` → `POST /predict` répond
3. `dotnet run` → `POST /api/demo/start` → poll `/api/status/{jobId}` → `GET /api/forecast`
4. Minikube : `helm install` → tous les pods `Running` → démo complète de bout en bout
