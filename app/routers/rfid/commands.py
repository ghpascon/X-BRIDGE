from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.device import device_responses, validate_device
from app.schemas.devices import devices

router = APIRouter(
    prefix=get_prefix_from_path(__file__), tags=[get_prefix_from_path(__file__)]
)


@router.post("/start/{device}")
async def start_inventory(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            print("[ START ]", msg)
            raise HTTPException(status_code=422, detail=msg)

        print(f"START -> {device}")
        await devices.start_inventory(device)
        return {"msg": msg}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.post("/stop/{device}")
async def stop_inventory(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            print("[ STOP ]", msg)
            raise HTTPException(status_code=422, detail=msg)

        print(f"STOP -> {device}")
        await devices.stop_inventory(device)
        return {"msg": msg}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.post("/clear/{device}")
async def clear_tags(device: str):
    print(f"CLEAR -> {device}")
    await devices.clear_tags(device)
    return {"msg": f"{device} clear tags"}


# @router.get("/set_gpo")
# async def set_gpo(request: Request):
#     state = request.query_params.get("state")

#     await reader.set_gpo(state=="true")

#     return {"message": "GPO command received", "state": state}

# @router.post("/write_epc")
# async def write_epc(
#     target_identifier: str = Form(...),
#     target_value: Optional[str] = Form(None),
#     new_epc: str = Form(...),
#     password: str = Form(...)
# ):
#     if target_identifier == "None":
#         target_value = None

#     alerts = await reader.write_epc(
#         {
#             "target_identifier": target_identifier,
#             "target_value": target_value,
#             "new_epc": new_epc,
#             "password": password,
#         }
#     )
#     print(alerts)
#     if alerts:
#         return RedirectResponse(f"/?msg={alerts[0]} &classe=alert-danger", 303)
#     return RedirectResponse("/", 303)
