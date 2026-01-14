from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path
from smartx_rfid.schemas.tag import TagSchema
from smartx_rfid.schemas.events import EventSchema

from app.services import rfid_manager

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post(
	'/tags/{device_name}',
	summary='Receive RFID tags',
	description='Endpoint to receive RFID tags from external sources.',
)
async def receive_tags(device_name: str, tags: list[TagSchema] | TagSchema):
	if isinstance(tags, TagSchema):
		tags = [tags]

	for tag in tags:
		rfid_manager.events.on_event(
			name=device_name, event_type='tag', event_data=tag.model_dump()
		)

	return JSONResponse(
		status_code=200,
		content={'message': 'Tags received successfully.', 'received_count': len(tags)},
	)


@router.post(
	'/events/{device_name}',
	summary='Receive RFID events',
	description='Endpoint to receive RFID events from external sources.',
)
async def receive_events(device_name: str, events: list[EventSchema] | EventSchema):
	if isinstance(events, EventSchema):
		events = [events]

	for event in events:
		rfid_manager.events.on_event(
			name=device_name,
			event_type=event.event_type,
			event_data=event.event_data,
		)

	return JSONResponse(
		status_code=200,
		content={'message': 'Events received successfully.', 'received_count': len(events)},
	)
