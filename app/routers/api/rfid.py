from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.path import get_prefix_from_path
from app.routers.rfid.commands import clear_tags, start_inventory, stop_inventory
from app.schemas.api.device import device_responses, validate_device, state_responses
from app.schemas.devices import devices

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post("/start/{device}", responses=device_responses)
async def api_start_inventory(device: str):
    return await start_inventory(device)


@router.post("/stop/{device}", responses=device_responses)
async def api_stop_inventory(device: str):
    return await stop_inventory(device)


@router.post("/clear/{device}", responses=device_responses)
async def api_clear_tags(device: str):
    return await clear_tags(device)


@router.post("/clear_all", responses=device_responses)
async def api_clear_all_tags():
    try:
        await devices.clear_tags()
        return {"msg": "success"}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.get("/get_device_state/{device}", responses=state_responses)
async def get_device_state(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            print("[ GET_DEVICE_STATE ]", msg)
            raise HTTPException(status_code=422, detail=msg)

        print(f"GET_DEVICE_STATE -> {device}")

        if not devices.devices.get(device).is_reading:
            return {"state": "idle"}
        else:
            return {"state": "running"}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.get("/get_report")
async def api_get_report(request: Request):
    return RedirectResponse(url=request.app.url_path_for("get_report"))
