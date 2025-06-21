from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.rfid import TagRequest, rfid_base_responses, InventoryRequest
import logging
from app.schemas.rfid import rfid

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post("/tag", responses=rfid_base_responses)
async def simulator_tag(tag: TagRequest):
    try:
        await rfid.on_tag(tag.model_dump())
        return {"msg": "success"}
    except Exception as e:
        logging.error(f"Erro ao processar tag: {e}")
        return JSONResponse(status_code=500, content={"msg": str(e)})


@router.post("/inventory", responses=rfid_base_responses)
async def simulator_inventory(inventory: InventoryRequest):
    try:
        if inventory.state:
            await rfid.on_start(inventory.device)
            return {"msg": f"{inventory.device} START"}
        else:
            await rfid.on_stop(inventory.device)
            return {"msg": f"{inventory.device} STOP"}
    except Exception as e:
        logging.error(f"Erro ao processar tag: {e}")
        return JSONResponse(status_code=500, content={"msg": str(e)})
