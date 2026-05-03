output "aks_name" {
  value = module.aks.cluster_name
}

output "storage_account_name" {
  value = module.storage.account_name
}

output "keyvault_uri" {
  value = module.keyvault.vault_uri
}

output "csi_client_id" {
  value = module.aks.csi_client_id
}
