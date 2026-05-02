resource "azurerm_storage_account" "sa" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "containers" {
  for_each             = toset(["raw", "processed", "models", "tfstate"])
  name                 = each.key
  storage_account_name = azurerm_storage_account.sa.name
}
