from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.rfid import TagRequest, rfid_base_responses, InventoryRequest, EventRequest
from app.schemas.rfid import rfid
import logging

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post(
    "/tag",
    responses=rfid_base_responses,
    summary="Simulate RFID tag read",
    description="Simulates an RFID tag being read and sends the data to the tag processing logic."
)
async def simulator_tag(tag: TagRequest):
    try:
        await rfid.on_tag(tag.model_dump())
        return {"msg": "success"}
    except Exception as e:
        logging.error(f"Error while processing tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/inventory",
    responses=rfid_base_responses,
    summary="Simulate inventory state",
    description="Starts or stops the inventory simulation for the specified device."
)
async def simulator_inventory(inventory: InventoryRequest):
    try:
        if inventory.state:
            await rfid.on_start(inventory.device)
            return {"msg": f"{inventory.device} STARTED"}
        else:
            await rfid.on_stop(inventory.device)
            return {"msg": f"{inventory.device} STOPPED"}
    except Exception as e:
        logging.error(f"Error while processing inventory simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/event",
    responses=rfid_base_responses,
    summary="Simulate an event",
    description="Simulate an event with a simulated data"
)
async def simulator_event(event: EventRequest):
    try:
        event_json = event.model_dump()
        await rfid.on_event(**event_json)
        return {"msg": f"Received event: {event_json}"}
    except Exception as e:
        logging.error(f"Error while processing event simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
