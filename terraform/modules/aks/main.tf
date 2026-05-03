resource "azurerm_kubernetes_cluster" "aks" {
  name                = "mlops-aks-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "mlops-${var.environment}"

  default_node_pool {
    name           = "default"
    node_count     = var.node_count
    vm_size        = var.vm_size
    vnet_subnet_id = var.subnet_id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "training" {
  name                  = "training"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_D4s_v3"
  node_count            = 0
  min_count             = 0
  max_count             = 1
  enable_auto_scaling   = true
  node_labels           = { pool = "training" }
}
