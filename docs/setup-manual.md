# Setup — Étapes manuelles et reste à faire

## Étapes réalisées manuellement

### Azure DevOps

- [x] Créer le projet **Meteo Brussel Prediction** sur `dev.azure.com/briacleguillou`
- [x] Pousser le repo local vers Azure Repos (`git remote add origin` + `git push`)
- [x] Créer un Personal Access Token (scope : Agent Pools Read & manage)
- [x] Créer le pool d'agents **local** (Project Settings → Agent pools)

### Agent self-hosted

- [x] Télécharger l'agent `vsts-agent-linux-x64-4.272.0.tar.gz`
- [x] Extraire dans `~/myagent`
- [x] Configurer l'agent (`./config.sh`) avec l'URL org et le PAT
- [x] Installer et démarrer comme service systemd (`./svc.sh install && start`)

### Code

- [x] Écrire `pipelines/ci.yml` (lint → tests → docker build + push)
- [x] Écrire `pipelines/release.yml` (terraform → helm → smoke test)
- [x] Écrire le chart Helm (`helm/mlops-stack/`)
- [x] Écrire les modules Terraform (`aks`, `storage`, `networking`, `keyvault`)

---

## Reste à faire

### Azure DevOps — Variables secrètes

Pipelines → **Library → New variable group** `mlops-secrets`, marquer comme secret :

- [ ] `DOCKER_USERNAME` — nom d'utilisateur Docker Hub
- [ ] `DOCKER_PASSWORD` — mot de passe Docker Hub
- [ ] `ARM_CLIENT_ID` — Service Principal Azure
- [ ] `ARM_CLIENT_SECRET` — Secret du Service Principal
- [ ] `ARM_SUBSCRIPTION_ID` — ID de la subscription Azure
- [ ] `ARM_TENANT_ID` — ID du tenant Azure

### Azure DevOps — Pipelines

- [ ] Créer le pipeline CI : Pipelines → New pipeline → Azure Repos → `pipelines/ci.yml`
- [ ] Créer le pipeline Release : Pipelines → New pipeline → Azure Repos → `pipelines/release.yml`
- [ ] Lier le variable group `mlops-secrets` aux deux pipelines

### Azure — Service Principal

```bash
az ad sp create-for-rbac --name mlops-sp --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

Copier `appId`, `password`, `tenant` → variables secrètes ci-dessus.

### Terraform — Configuration

- [ ] Remplir `tenant_id` dans `terraform/environments/dev.tfvars` et `prod.tfvars`
- [ ] Créer manuellement le storage account pour le backend Terraform (bootstrap unique) :

  ```bash
  az group create -n mlops-tfstate -l westeurope
  az storage account create -n mlopstfstate -g mlops-tfstate --sku Standard_LRS
  az storage container create -n tfstate --account-name mlopstfstate
  ```

### Docker Hub

- [ ] Construire et pousser les 4 images une première fois manuellement (avant le premier run CI) :

  ```bash
  docker build -f .docker/python-base.Dockerfile -t briacleguillou/python-base:latest .
  docker build -f .docker/trainer.Dockerfile -t briacleguillou/trainer:latest .
  docker build -f .docker/worker.Dockerfile -t briacleguillou/worker:latest .
  docker build -f .docker/orchestrator.Dockerfile -t briacleguillou/orchestrator:latest .
  docker push briacleguillou/python-base:latest
  docker push briacleguillou/trainer:latest
  docker push briacleguillou/worker:latest
  docker push briacleguillou/orchestrator:latest
  ```

### Kubernetes — Secret CSI

- [ ] Installer le CSI driver sur AKS après `terraform apply` :

  ```bash
  az aks enable-addons --addons azure-keyvault-secrets-provider \
    -n mlops-aks-dev -g mlops-dev
  ```

### Validation finale

- [ ] `docker compose --profile dev run --rm python-dev tests/trainer tests/worker -v` → vert
- [ ] `docker compose --profile dev run --rm dotnet-dev` → vert
- [ ] Premier run CI déclenché sur push → vert
- [ ] Premier run Release (dev) → `terraform apply` + `helm upgrade` → pods Running
- [ ] Flow complet : `POST /api/demo/start` → poll status → `GET /api/forecast`
