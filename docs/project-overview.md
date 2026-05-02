# Meteo Brussel Prediction — Présentation du projet

## Objectif

Prévoir la température à Bruxelles sur les 14 prochains jours à l'aide d'un modèle LSTM entraîné sur les données historiques Open-Meteo. Le pipeline complet — collecte, entraînement, inférence — est déclenché manuellement via une API REST.

---

## Architecture

```
[Utilisateur]
     │
     ▼
POST /api/demo/start
     │
     ├─► OpenMeteoService → fetch 90 jours de températures
     ├─► BlobService      → upload raw/brussels.csv (Azure Blob)
     └─► K8sJobService    → crée un Job Kubernetes (trainer)

[Job Kubernetes — node pool "training"]
     │
     └─► train.py : télécharge CSV → LSTM 50 epochs → upload models/lstm_vN.pt

GET /api/status/{jobId}
     │
     └─► si Succeeded → WorkerService.ReloadAsync() (charge le nouveau modèle)

GET /api/forecast
     │
     └─► WorkerService.PredictAsync() → 14 températures prévues
```

---

## Composants

| Composant | Technologie | Rôle |
|---|---|---|
| **Orchestrateur** | .NET 8 Web API | Point d'entrée unique, orchestre le flow |
| **Trainer** | Python / PyTorch | Entraîne le LSTM, upload le modèle |
| **Worker** | Python / FastAPI | Charge le modèle, répond aux requêtes de prévision |
| **Infrastructure** | Azure AKS + Blob + Key Vault | Compute Kubernetes, stockage, secrets |

### Modèle LSTM

- Input : 30 jours de températures normalisées
- Architecture : 2 couches LSTM (hidden=64) + couche linéaire
- Output : 14 températures prévues (dénormalisées)
- Entraînement : 50 epochs, MSE loss, Adam optimizer

---

## Infrastructure

```
Azure
├── AKS (2 node pools)
│   ├── default      — orchestrateur + worker (always-on)
│   └── training     — trainer job (autoscale 0→1)
├── Blob Storage
│   ├── raw/         — données brutes CSV
│   ├── models/      — modèles .pt versionnés
│   └── tfstate/     — état Terraform
└── Key Vault        — secrets montés via CSI driver
```

---

## Stack technique

- **Python** : PyTorch, FastAPI, pandas, azure-storage-blob
- **Backend** : .NET 8, KubernetesClient, Azure.Storage.Blobs
- **Infrastructure** : Terraform, Helm, Azure DevOps Pipelines
- **CI/CD** : Agent self-hosted sur machine locale, Docker Hub

---

## Flow complet

1. `POST /api/demo/start` → collecte + stockage + lancement du Job → `202 {jobId}`
2. `GET /api/status/{jobId}` → poll jusqu'à `Succeeded` → reload automatique du worker
3. `GET /api/forecast` → prévision 14 jours
