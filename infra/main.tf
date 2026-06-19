provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "vector_triage"
  location = var.location
}
