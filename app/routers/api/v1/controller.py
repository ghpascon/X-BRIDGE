from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path
from app.schemas.write_list import WriteListPrefixModel
from app.services import rfid_manager
from app.schemas.renner import InventoryModel

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.get(
	'/controller_info',
	summary='Get RFID info',
)
async def controller_info():
	controller = rfid_manager.controller

	# Monta dict nome: tipo para atributos e métodos públicos
	info = {}
	for name in dir(controller):
		if name.startswith('_'):
			continue
		attr = getattr(controller, name)
		if callable(attr):
			info[name] = f'function ({type(attr).__name__})'
		else:
			info[name] = type(attr).__name__
	return info


# [WRITE LIST]
@router.get(
	'/get_write_list',
	summary='Get write list from RFID controller',
)
async def get_write_list():
	return rfid_manager.controller.write_list


@router.post(
	'/create_write_list_prefix',
	summary='Write a list of tags to the RFID controller',
)
async def create_write_list_prefix(write_list: WriteListPrefixModel):
	write_list = rfid_manager.controller.create_write_list_prefix(
		write_list.epcs, write_list.prefix
	)
	if not write_list:
		return JSONResponse(
			status_code=400, content={'message': 'Tags not found in current tag list'}
		)
	return write_list


@router.post(
	'/add_to_write_list/{tid}/{target}',
	summary='Add a tag to the write list in the RFID controller',
)
async def add_to_write_list(tid: str, target: str):
	tag = rfid_manager.controller.tags.get_by_identifier(tid.lower(), identifier_type='tid')
	if not tag:
		return JSONResponse(status_code=404, content={'message': f'Tag {tid} not found'})
	rfid_manager.controller.add_to_write_list(tag, target)
	return {'message': f'Tag {tid} added to write list with target {target} successfully'}


@router.post(
	'/clear_write_list',
	summary='Clear the write list in the RFID controller',
)
async def clear_write_list():
	rfid_manager.controller.clear_write_list()
	return {'message': 'Write list cleared successfully'}


@router.delete(
	'/delete_tid_from_write_list/{tid}',
	summary='Delete a tag from the write list in the RFID controller',
)
async def delete_tid_from_write_list(tid: str):
	tag = rfid_manager.controller.tags.get_by_identifier(tid.lower(), identifier_type='tid')
	if not tag:
		return JSONResponse(status_code=404, content={'message': f'Tag {tid} not found'})
	success = rfid_manager.controller.remove_from_write_list(tag)
	if success:
		return {'message': f'Tag {tid} removed from write list successfully'}
	else:
		return JSONResponse(
			status_code=400, content={'message': f'Failed to remove tag {tid} from write list'}
		)


# INVENTORY
@router.get(
	'/get_inventory_table',
	summary='Get the inventory table from the RFID controller',
)
async def get_inventory_table(limit: int = 999999, offset: int = 0):
	return rfid_manager.controller.get_inventory_table(limit=limit, offset=offset)


@router.get(
	'/get_sku/{sku}',
	summary='Get inventory details for a specific SKU from the RFID controller',
)
async def get_inventory(sku: str):
	return rfid_manager.controller.get_sku(sku)


@router.get(
	'/get_quantity/{sku}',
	summary='Get the quantity for a specific SKU from the RFID controller',
)
async def get_quantity(sku: str):
	return rfid_manager.controller.get_quantity(sku)


@router.post(
	'/add_to_inventory',
	summary='Add inventory data to the RFID controller',
)
async def add_to_inventory(data: list[InventoryModel] | InventoryModel):
	if not isinstance(data, list):
		data = [data]
	if not all(isinstance(item, InventoryModel) for item in data):
		return JSONResponse(status_code=400, content={'message': 'Invalid inventory data'})
	success = rfid_manager.controller.add_inventory([item.model_dump() for item in data])
	if success:
		return {'message': 'Inventory added successfully'}
	else:
		return JSONResponse(status_code=400, content={'message': 'Failed to add inventory'})


@router.put(
	'/update_quantity/{sku}/{quantity}',
	summary='Update the quantity for a specific SKU in the RFID controller',
)
async def update_quantity(sku: str, quantity: int):
	success = rfid_manager.controller.update_quantity(sku, quantity)
	if success:
		return {'message': f'Quantity for SKU {sku} updated successfully'}
	else:
		return JSONResponse(
			status_code=400, content={'message': f'Failed to update quantity for SKU {sku}'}
		)


@router.delete(
	'/delete_sku/{sku}',
	summary='Delete a specific SKU from the RFID controller',
)
async def delete_sku(sku: str):
	success = rfid_manager.controller.delete_sku(sku)
	if success:
		return {'message': f'SKU {sku} deleted successfully'}
	else:
		return JSONResponse(status_code=400, content={'message': f'Failed to delete SKU {sku}'})


@router.delete(
	'/clear_inventory_table',
	summary='Clear the entire inventory table from the RFID controller',
)
async def clear_inventory_table():
	success = rfid_manager.controller.clear_inventory_table()
	if success:
		return {'message': 'Inventory table cleared successfully'}
	else:
		return JSONResponse(status_code=400, content={'message': 'Failed to clear inventory table'})
