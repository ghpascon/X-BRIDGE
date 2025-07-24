from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import RedirectResponse
from typing import List, Union

from app.core.path import get_prefix_from_path
from app.routers.rfid.commands import (
    clear_tags,
    start_inventory,
    stop_inventory,
    set_gpo,
)
from app.schemas.api.device import device_responses, validate_device, state_responses
from app.schemas.api.rfid import SetGpoRequest, gpo_responses, rfid_base_responses, TagRequest, EventRequest
from app.schemas.devices import devices
from app.schemas.events import events
import asyncio

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post(
    "/start/{device}",
    responses=device_responses,
    summary="Start tag inventory",
    description="Starts the tag inventory process for the specified RFID reader.",
)
async def api_start_inventory(device: str):
    return await start_inventory(device)


@router.post(
    "/stop/{device}",
    responses=device_responses,
    summary="Stop tag inventory",
    description="Stops the tag inventory process for the specified RFID reader.",
)
async def api_stop_inventory(device: str):
    return await stop_inventory(device)


@router.post(
    "/clear/{device}",
    responses=device_responses,
    summary="Clear tags from device",
    description="Clears the tag list for the specified device.",
)
async def api_clear_tags(device: str):
    return await clear_tags(device)


@router.post(
    "/clear_all",
    responses=device_responses,
    summary="Clear tags from all devices",
    description="Clears the tag lists from all connected devices.",
)
async def api_clear_all_tags():
    try:
        await devices.clear_tags()
        return {"msg": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/receive_tags",
    summary="Receive tags from external devices",
    description="Receives either a single tag or a list of tags",
)
async def receive_tags(tags: Union[TagRequest, List[TagRequest]] = Body(...)):
    tags = tags if isinstance(tags, list) else [tags]
    for tag in tags:
        try:
            await events.on_tag(tag.model_dump()) 
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 

    return {"msg": "success"}

@router.post(
    "/receive_events",
    summary="Receive events from external devices",
    description="Receives either a single event or a list of events",
)
async def receive_events(events_received: Union[EventRequest, List[EventRequest]] = Body(...)):
    print(events_received)
    events_received = events_received if isinstance(events_received, list) else [events_received]
    print(events_received)
    for event in events_received:
        event = event.model_dump()
        if event.get("event_type") == "tag":
            asyncio.create_task(events.on_tag(event.get("event_data")))
        else:
            asyncio.create_task(events.on_event(**event))
    return {"msg": "success"}

@router.post(
    "/set_gpo/{device}",
    responses=gpo_responses,
    summary="Set GPO state",
    description="Sends a GPO command to the device with the given parameters.",
)
async def api_set_gpo(device: str, data: SetGpoRequest):
    data = data.model_dump()
    return await set_gpo(
        device,
        data.get("gpo_pin", 1),
        data.get("state", True),
        data.get("control", "static"),
        data.get("time", 1000),
    )


@router.get(
    "/get_device_state/{device}",
    responses=state_responses,
    summary="Get device state",
    description="Returns the current reading state (`connected` or `running`) of the specified device.",
)
async def get_device_state(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            raise HTTPException(status_code=422, detail=msg)

        if (
            hasattr(devices.devices.get(device), "is_reading")
            and devices.devices.get(device).is_reading
        ):
            return {"state": "running"}
        else:
            return {"state": "connected"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/get_report",
    summary="Get the report",
    description="Get the report of the tags and events.",
)
async def api_get_report(request: Request):
    return RedirectResponse(url=request.app.url_path_for("get_report"))
