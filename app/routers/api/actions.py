from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.rfid import (
    RfidRequest,
    rfid_actions_responses,
    rfid_base_responses,
)
from app.schemas.devices import devices
from app.schemas.rfid import rfid
from app.core.config import settings

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.get("/get_actions", responses=rfid_actions_responses)
async def get_actions():
    try:
        return rfid.actions
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": str(e)})


@router.post("/set_actions", responses=rfid_actions_responses)
async def set_actions(data: RfidRequest):
    try:
        data = data.model_dump()
        await rfid.set_actions(data)
        settings.load()
        return {"msg": "success", "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": str(e)})
