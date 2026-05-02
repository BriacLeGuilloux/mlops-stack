terraform {
  backend "azurerm" {
    resource_group_name  = "mlops-tfstate"
    storage_account_name = "mlopstfstate"
    container_name       = "tfstate"
    key                  = "mlops.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}
