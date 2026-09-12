from pydantic import BaseModel, Field


class InventoryModel(BaseModel):
	sku: str = Field(..., description='SKU of the inventory item')
	quantity: int = Field(..., description='Quantity of the inventory item')
