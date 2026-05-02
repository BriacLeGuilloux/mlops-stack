# Terraform — Explication et configuration

## Pourquoi Terraform ?

Terraform permet de décrire l'infrastructure Azure en code (fichiers `.tf`) plutôt que de la créer manuellement via le portail. Avantages :

- Reproductible : le même code crée la même infrastructure en dev et en prod
- Versionné : les changements d'infrastructure sont tracés dans git
- Automatisé : le pipeline Release lance `terraform apply` sans intervention manuelle

---

## Le problème du state

Terraform maintient un fichier `terraform.tfstate` qui représente l'état actuel de l'infrastructure. Il doit être **partagé** entre toutes les personnes et machines qui utilisent Terraform (ton PC, l'agent Azure DevOps, un collègue).

**Solution : stocker le state dans Azure Blob Storage.**

C'est ce que configure `terraform/backend.tf` :

```hcl
backend "azurerm" {
  resource_group_name  = "mlops-tfstate"
  storage_account_name = "mlopsbriacstate"
  container_name       = "tfstate"
  key                  = "mlops.tfstate"
}
```

---

## Le bootstrap

Le state doit être stocké quelque part — mais Terraform ne peut pas créer ce storage account lui-même (il aurait besoin d'un state pour le faire). C'est le **problème du bootstrap** : il faut créer ce storage account manuellement une seule fois.

C'est ce que tu as fait avec ces commandes :

```bash
# 1. Créer un resource group dédié au state Terraform
az group create -n mlops-tfstate -l westeurope

# 2. Créer le storage account
az storage account create -n mlopsbriacstate -g mlops-tfstate --sku Standard_LRS

# 3. Créer le container blob qui accueillera le fichier state
az storage container create -n tfstate --account-name mlopsbriacstate --auth-mode login
```

Cette opération est **unique** — elle ne se refait jamais.

---

## Structure des modules

```
terraform/
├── backend.tf          → connexion au state distant
├── variables.tf        → déclaration des paramètres
├── main.tf             → appelle les 4 modules
├── outputs.tf          → valeurs exportées après apply
├── environments/
│   ├── dev.tfvars      → valeurs pour l'environnement dev
│   └── prod.tfvars     → valeurs pour l'environnement prod
└── modules/
    ├── networking/     → VNet + subnet
    ├── aks/            → cluster Kubernetes + node pools
    ├── storage/        → Blob Storage (données + modèles)
    └── keyvault/       → Key Vault + secrets
```

### Ce que chaque module crée

| Module | Ressources Azure |
|---|---|
| `networking` | Virtual Network, Subnet |
| `aks` | AKS cluster, node pool `default`, node pool `training` (autoscale 0→1) |
| `storage` | Storage Account, containers `raw/`, `processed/`, `models/`, `tfstate` |
| `keyvault` | Key Vault, access policy pour AKS, secret `azure-storage-conn-str` |

---

## Utilisation

Le pipeline Release lance automatiquement :

```bash
terraform init   # connexion au backend Azure
terraform apply -var-file=environments/dev.tfvars
```

Pour lancer manuellement depuis ton PC :

```bash
cd terraform
az login
terraform init
terraform apply -var-file=environments/dev.tfvars
```

---

## Environnements

Les fichiers `dev.tfvars` et `prod.tfvars` contiennent les valeurs spécifiques à chaque environnement (nom du resource group, taille des VMs, nombre de nodes, etc.). Le code Terraform est le même — seules les valeurs changent.
