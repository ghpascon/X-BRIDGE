from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path

from app.services import rfid_manager

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


@router.get(
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
