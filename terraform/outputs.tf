output "aks_name"             { value = azurerm_kubernetes_cluster.aks.name }
output "storage_account_name" { value = azurerm_storage_account.sa.name }
output "keyvault_uri"         { value = azurerm_key_vault.kv.vault_uri }
output "csi_client_id"        { value = azurerm_kubernetes_cluster.aks.key_vault_secrets_provider[0].secret_identity[0].client_id }
