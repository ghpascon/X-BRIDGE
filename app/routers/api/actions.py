from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.rfid import (
    RfidRequest,
    rfid_actions_responses,
)
from app.schemas.devices import devices
from app.schemas.events import events
from app.core.config import settings

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.get(
    "/get_actions",
    responses=rfid_actions_responses,
    summary="Get current RFID actions",
    description="Returns the list of currently configured RFID actions for all connected devices.",
)
async def get_actions():
    """
    Retrieve the currently configured actions for the RFID system.
    """
    try:
        return events.actions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/set_actions",
    responses=rfid_actions_responses,
    summary="Set RFID actions",
    description="Sets or updates the configured RFID actions and reloads application settings.",
)
async def set_actions(data: RfidRequest):
    """
    Set new RFID actions using the provided request data.
    Reloads the system settings after applying the configuration.
    """
    try:
        data = data.model_dump()
        await events.set_actions(data)
        settings.load()
        return {"msg": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
