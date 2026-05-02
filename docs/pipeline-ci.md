# Pipeline CI — Explication

## Rôle

Le pipeline CI (Continuous Integration) s'assure qu'à chaque push sur `main`, le code est valide, les tests passent, et les images Docker sont à jour sur Docker Hub.

Il tourne sur **ton PC** via l'agent self-hosted `local` installé dans `~/myagent`.

---

## Déclenchement

```yaml
trigger:
  branches:
    include:
      - main
```

Le pipeline se lance automatiquement à chaque push sur la branche `main`. Il ne se déclenche pas sur les autres branches.

---

## Agent d'exécution

```yaml
pool:
  name: local
```

Toutes les étapes s'exécutent sur ton PC (pool `local`), pas sur les serveurs Microsoft. Ton Docker, tes images locales et ton réseau sont utilisés directement.

---

## Stage 1 — Lint Python

**Objectif :** vérifier que le code Python respecte les conventions de style.

### ruff

```bash
docker compose --profile dev build python-dev
docker compose --profile dev run --rm python-dev -m ruff check python/
```

- Construit l'image `python-dev` si elle n'existe pas
- Lance `ruff` sur tout le dossier `python/`
- `ruff` vérifie : imports inutilisés, variables non utilisées, mauvaises pratiques, etc.
- Si une erreur est trouvée → le pipeline s'arrête

### black

```bash
docker compose --profile dev run --rm python-dev -m black --check python/
```

- `black` vérifie le **formatage** du code (indentation, longueur des lignes, guillemets, etc.)
- `--check` ne modifie rien — il retourne une erreur si le code n'est pas formaté correctement

---

## Stage 2 — Tests

**Objectif :** s'assurer que le code fonctionne correctement. Ne démarre que si le Lint passe (`dependsOn: Lint`).

Les deux jobs s'exécutent **en parallèle**.

### Python tests

```bash
docker compose --profile dev run --rm python-dev tests/trainer tests/worker -v
```

Lance `pytest` dans le conteneur `python-dev` sur :
- `tests/trainer/` → teste le modèle LSTM et les fonctions d'entraînement
- `tests/worker/` → teste les endpoints FastAPI (`/predict`, `/reload`)

### .NET tests

```bash
docker compose --profile dev run --rm dotnet-dev
```

Lance `dotnet test` sur `orchestrator/orchestrator.sln` dans le conteneur .NET SDK :
- `DemoControllerTests` → teste `POST /api/demo/start`
- `StatusControllerTests` → teste `GET /api/status/{jobId}`

---

## Stage 3 — Build & Push

**Objectif :** construire les 4 images Docker et les pousser sur Docker Hub. Ne démarre que si les tests passent (`dependsOn: Test`).

### Docker login

```bash
echo "$(DOCKER_PASSWORD)" | docker login -u "$(DOCKER_USERNAME)" --password-stdin
```

S'authentifie sur Docker Hub avec les variables secrètes du variable group `mlops-secrets`. Le mot de passe est passé via `stdin` pour éviter qu'il apparaisse dans les logs.

### Build des images (dans l'ordre)

```
python-base → trainer
           → worker
orchestrator (indépendant)
```

L'ordre est important : `trainer` et `worker` dépendent de `python-base`, donc `python-base` est buildé en premier.

### Push sur Docker Hub

```bash
docker push briacleguillou/python-base:latest
docker push briacleguillou/trainer:latest
docker push briacleguillou/worker:latest
docker push briacleguillou/orchestrator:latest
```

Les 4 images sont poussées sous le tag `latest`. Le pipeline Release utilisera ensuite ces images pour déployer sur AKS.

---

## Résumé du flow

```
push sur main
     │
     ▼
[Lint Python]
  ├─ ruff   → erreurs de code ?
  └─ black  → formatage correct ?
     │ si tout passe
     ▼
[Tests] (en parallèle)
  ├─ pytest       → trainer + worker OK ?
  └─ dotnet test  → orchestrateur OK ?
     │ si tout passe
     ▼
[Build & Push]
  ├─ docker build × 4
  └─ docker push × 4 → Docker Hub
```

Si n'importe quelle étape échoue, le pipeline s'arrête et Azure DevOps notifie par email.
