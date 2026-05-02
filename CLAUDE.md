# CLAUDE.md — MLOps Stack

## Projet

Prévision de température à Bruxelles sur 14 jours (LSTM PyTorch), déclenchée manuellement depuis un .NET 8 Web API qui orchestre collecte → stockage → entraînement → inférence.

Voir [docs/architecture.md](docs/architecture.md) pour la vue d'ensemble complète.

---

## Runtime local

Python et .NET ne sont pas installés sur le host. Utiliser Docker pour tout exécuter :

```bash
# Trainer
docker compose run --rm trainer python train.py

# Worker
docker compose run --rm worker

# Orchestrateur
docker compose run --rm orchestrator
```

---

## Tests

```bash
# Python — depuis la racine
docker compose run --rm python-dev pytest tests/trainer tests/worker -v

# .NET
docker compose run --rm dotnet-dev dotnet test orchestrator.sln
```

---

## Build des images

```bash
docker build -f .docker/python-base.Dockerfile -t briacleguillou/python-base:latest .
docker build -f .docker/trainer.Dockerfile -t briacleguillou/trainer:latest .
docker build -f .docker/worker.Dockerfile -t briacleguillou/worker:latest .
docker build -f .docker/orchestrator.Dockerfile -t briacleguillou/orchestrator:latest .
```

---

## Variables d'environnement

| Variable | Composant | Description |
| --- | --- | --- |
| `AZURE_STORAGE_CONN_STR` | trainer, worker | Connection string Azure Blob Storage |
| `BLOB_CONTAINER` | trainer, worker | Nom du container blob (ex: `mlops`) |
| `WORKER_URL` | orchestrator | URL interne du worker FastAPI |
| `KUBECONFIG` | orchestrator | Chemin vers le kubeconfig |
| `OPENMETEO_BASE_URL` | orchestrator | URL de base Open-Meteo (défaut: `https://api.open-meteo.com`) |

---

## Structure

```text
.docker/        Dockerfiles des 4 images
python/         Code source Python (trainer, worker)
tests/          Tous les tests (trainer, worker, orchestrator)
orchestrator/   .NET 8 Web API
helm/           Chart Helm
terraform/      IaC (modules: aks, storage, networking, keyvault)
pipelines/      Pipelines Azure DevOps (ci.yml, release.yml)
docs/           Documentation (architecture.md)
```

---

## Conventions

- Commits : Conventional Commits (`feat(scope): ...`)
- Python : `ruff` + `black`, type hints obligatoires
- .NET : options pattern, injection de dépendances, pas de `static`
- Pas de secrets dans le code — tout via env vars ou Key Vault
