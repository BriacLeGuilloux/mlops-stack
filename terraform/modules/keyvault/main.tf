data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "kv" {
  name                = var.keyvault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = data.azurerm_client_config.current.object_id
    secret_permissions = ["Get", "Set", "Delete", "List"]
  }

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = var.aks_identity_id
    secret_permissions = ["Get", "List"]
  }

  access_policy {
    tenant_id          = var.tenant_id
    object_id          = var.csi_identity_id
    secret_permissions = ["Get", "List"]
  }
}

resource "azurerm_key_vault_secret" "storage_conn_str" {
  name         = "azure-storage-conn-str"
  value        = var.storage_connection_string
  key_vault_id = azurerm_key_vault.kv.id
}
