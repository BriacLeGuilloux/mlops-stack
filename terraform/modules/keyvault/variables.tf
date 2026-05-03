variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "environment" { type = string }
variable "keyvault_name" { type = string }
variable "tenant_id" { type = string }
variable "aks_identity_id" { type = string }
variable "csi_identity_id" { type = string }
variable "storage_connection_string" {
  type      = string
  default   = ""
  sensitive = true
}
