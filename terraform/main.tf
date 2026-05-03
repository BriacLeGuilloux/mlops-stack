module "networking" {
  source              = "./modules/networking"
  resource_group_name = var.resource_group_name
  location            = var.location
  environment         = var.environment
}

module "aks" {
  source              = "./modules/aks"
  resource_group_name = var.resource_group_name
  location            = var.location
  environment         = var.environment
  subnet_id           = module.networking.subnet_id
  node_count          = var.aks_node_count
  vm_size             = var.aks_vm_size
}

module "storage" {
  source               = "./modules/storage"
  resource_group_name  = var.resource_group_name
  location             = var.location
  environment          = var.environment
  storage_account_name = var.storage_account_name
  depends_on           = [module.networking]
}

module "keyvault" {
  source                    = "./modules/keyvault"
  resource_group_name       = var.resource_group_name
  location                  = var.location
  environment               = var.environment
  keyvault_name             = var.keyvault_name
  tenant_id                 = var.tenant_id
  aks_identity_id           = module.aks.kubelet_identity_id
  csi_identity_id           = module.aks.csi_object_id
  storage_connection_string = module.storage.connection_string
}
