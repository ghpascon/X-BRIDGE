from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path

from app.services import rfid_manager
from app.models import get_all_models

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.get(
	'/get_tags',
	summary='Get all tags',
	description='Returns a list of all detected RFID tags.',
)
async def get_tags():
	return rfid_manager.events.tags.get_all()


@router.get(
	'/get_tag_count',
	summary='Get tag count',
	description='Returns the total number of detected RFID tags.',
)
async def get_tag_count():
	return {'count': len(rfid_manager.events.tags)}


@router.post(
	'/clear_tags',
	summary='Clear all tags',
	description='Removes all detected RFID tags from the system.',
)
async def clear_tags():
	rfid_manager.events.tags.clear()
	return JSONResponse(
		status_code=200,
		content={'message': 'All tags have been cleared.'},
	)


@router.get(
	'/get_epcs',
	summary='Get all EPCs',
	description='Returns a list of all detected EPCs from RFID tags.',
)
async def get_epcs():
	return rfid_manager.events.tags.get_epcs()


@router.get(
	'/get_gtin_count',
	summary='Get GTIN count',
	description='Returns the total number of unique GTINs from detected RFID tags.',
)
async def get_gtin_count():
	return rfid_manager.events.tags.get_gtin_counts()


@router.get(
	'/get_tag_info/{epc}',
	summary='Get tag information',
	description='Returns detailed information about detected RFID tags.',
)
async def get_tag_info(epc: str):
	return rfid_manager.events.tags.get_by_identifier(identifier_value=epc, identifier_type='epc')


@router.get(
	'/generate_table_report/{table_name}',
	summary='Generate table report',
	description='Generates a report for a specified database table.',
)
async def generate_table_report(table_name: str, limit: int = 1000, offset: int = 0):
	# Validate table
	models = get_all_models()
	valid_table = False
	table_model = None
	for model in models:
		if table_name == model.__tablename__:
			valid_table = True
			table_model = model
			break

	if not valid_table:
		return JSONResponse(status_code=400, content={'error': 'Invalid table name'})

	try:
		return rfid_manager.events.integration.generate_table_report(
			model=table_model, limit=limit, offset=offset
		)
	except Exception as e:
		return JSONResponse(status_code=500, content={'error': str(e)})
