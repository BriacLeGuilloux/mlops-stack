variable "location"             { type = string; default = "westeurope" }
variable "environment"          { type = string }
variable "resource_group_name"  { type = string }
variable "storage_account_name" { type = string }
variable "keyvault_name"        { type = string }
variable "tenant_id"            { type = string }
variable "aks_node_count"       { type = number; default = 1 }
variable "aks_vm_size"          { type = string; default = "Standard_B2s_v2" }
