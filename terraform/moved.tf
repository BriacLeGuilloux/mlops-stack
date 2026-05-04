moved {
  from = module.networking.azurerm_resource_group.rg
  to   = azurerm_resource_group.rg
}

moved {
  from = module.networking.azurerm_virtual_network.vnet
  to   = azurerm_virtual_network.vnet
}

moved {
  from = module.networking.azurerm_subnet.aks
  to   = azurerm_subnet.aks
}

moved {
  from = module.aks.azurerm_kubernetes_cluster.aks
  to   = azurerm_kubernetes_cluster.aks
}

moved {
  from = module.aks.azurerm_kubernetes_cluster_node_pool.training
  to   = azurerm_kubernetes_cluster_node_pool.training
}

moved {
  from = module.storage.azurerm_storage_account.sa
  to   = azurerm_storage_account.sa
}

moved {
  from = module.storage.azurerm_storage_container.containers
  to   = azurerm_storage_container.containers
}

moved {
  from = module.keyvault.azurerm_key_vault.kv
  to   = azurerm_key_vault.kv
}

moved {
  from = module.keyvault.azurerm_key_vault_secret.storage_conn_str
  to   = azurerm_key_vault_secret.storage_conn_str
}
