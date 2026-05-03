locals {
  prefix = "mlops-${var.environment}"
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Networking
resource "azurerm_virtual_network" "vnet" {
  name                = "${local.prefix}-vnet"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# AKS
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${local.prefix}-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = local.prefix
  oidc_issuer_enabled = true

  default_node_pool {
    name           = "default"
    node_count     = var.aks_node_count
    vm_size        = var.aks_vm_size
    vnet_subnet_id = azurerm_subnet.aks.id
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = false
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin = "azure"
    service_cidr   = "10.1.0.0/16"
    dns_service_ip = "10.1.0.10"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "training" {
  name                  = "training"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_D4s_v3"
  vnet_subnet_id        = azurerm_subnet.aks.id
  node_count            = 0
  min_count             = 0
  max_count             = 1
  enable_auto_scaling   = true
  node_labels           = { pool = "training" }
}

# Storage
resource "azurerm_storage_account" "sa" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "containers" {
  for_each             = toset(["raw", "processed", "models", "tfstate"])
  name                 = each.key
  storage_account_name = azurerm_storage_account.sa.name
}

# Key Vault
resource "azurerm_key_vault" "kv" {
  name                = var.keyvault_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = data.azurerm_client_config.current.object_id
    secret_permissions = ["Get", "Set", "Delete", "List"]
  }

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
    secret_permissions = ["Get", "List"]
  }

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = azurerm_kubernetes_cluster.aks.key_vault_secrets_provider[0].secret_identity[0].object_id
    secret_permissions = ["Get", "List"]
  }
}

resource "azurerm_key_vault_secret" "storage_conn_str" {
  name         = "azure-storage-conn-str"
  value        = azurerm_storage_account.sa.primary_connection_string
  key_vault_id = azurerm_key_vault.kv.id
}
