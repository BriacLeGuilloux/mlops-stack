output "account_name" {
  value = azurerm_storage_account.sa.name
}

output "connection_string" {
  value     = azurerm_storage_account.sa.primary_connection_string
  sensitive = true
}
