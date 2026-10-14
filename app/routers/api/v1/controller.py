from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path
from app.schemas.write_list import WriteListPrefixModel
from app.services import rfid_manager

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


# HELPER FUNCTIONS - Placeholder
@router.get(
	'/get_value_placeholder',
	summary='Get a value for placeholder',
)
async def get_value_placeholder():
	return {
		'value': 'ABC',
		'description': 'This is a placeholder value',
		'qty': 10,
		'dict': {'key1': 'value1', 'key2': 'value2'},
		'list': [1, 2, 3],
		'table': [
			{'column1': 'value1', 'column2': 'value2'},
			{'column1': 'value3', 'column2': 'value4'},
		],
	}


@router.delete(
	'/delete_value_placeholder',
	summary='Delete the value for placeholder',
)
async def delete_value_placeholder():
	return {'message': 'Value for placeholder deleted successfully'}


@router.post(
	'/set_value_placeholder/{value}',
	summary='Set a value for placeholder',
)
async def set_value_placeholder(value: str):
	if not value:
		return JSONResponse(status_code=400, content={'message': 'Value cannot be empty'})
	return {'message': f'Value set to {value} successfully'}


@router.post(
	'/receive_from_file',
	summary='Set values for placeholder from uploaded file',
)
async def receive_from_file(items: list[dict]):
	if not items:
		return JSONResponse(status_code=400, content={'message': 'Payload cannot be empty'})

	print(f'Received items from file: {items}')
	return {
		'message': 'Values received successfully',
		'received_count': len(items),
		'preview': items[:5],
	}
