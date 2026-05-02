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

---

## Reste à faire

### Pipelines Azure DevOps

- [ ] Écrire `pipelines/ci.yml` (lint → tests → docker build + push)
- [ ] Écrire `pipelines/release.yml` (terraform → helm → smoke test)
- [ ] Créer les variables secrètes dans Azure DevOps :
  - `DOCKER_USERNAME` / `DOCKER_PASSWORD` (Docker Hub)
  - `AZURE_STORAGE_CONN_STR`
- [ ] Créer les pipelines dans Azure DevOps UI (Pipelines → New pipeline → Azure Repos → YAML existant)

### Infrastructure Azure (Terraform)

- [ ] Écrire les modules Terraform (`aks`, `storage`, `networking`, `keyvault`)
- [ ] Créer un Service Principal Azure avec les droits nécessaires
- [ ] Configurer le backend Terraform (container `tfstate` dans Azure Blob)
- [ ] Ajouter la service connection Azure dans Azure DevOps (Project Settings → Service connections)

### Kubernetes (Helm)

- [ ] Écrire le chart Helm (`helm/mlops-stack/`)
- [ ] Créer le secret Kubernetes `mlops-secrets` avec `AZURE_STORAGE_CONN_STR`
- [ ] Valider le déploiement sur Minikube avant AKS

### Docker Hub

- [ ] Vérifier que les images sont publiques (ou configurer imagePullSecrets sur AKS)
- [ ] Construire et pousser les 4 images une première fois manuellement

### Validation finale

- [ ] `docker compose --profile dev run --rm python-dev tests/trainer tests/worker -v` → vert
- [ ] `docker compose --profile dev run --rm dotnet-dev` → vert
- [ ] Flow complet : `POST /api/demo/start` → poll status → `GET /api/forecast`
