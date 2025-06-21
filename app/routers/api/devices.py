from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.device import (
    config_responses,
    device_list_responses,
    validate_device,
)
from app.schemas.devices import devices

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.get("/get_device_list", responses=device_list_responses)
async def api_get_device_list():
    return devices.get_device_list()


@router.get("/get_device_config/{device_name}", responses=config_responses)
async def get_device_config(device_name: str):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return devices.devices.get(device_name).config
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": "Internal Error"})


@router.get("/get_device_types_list", responses=device_list_responses)
async def api_get_device_types_list():
    return await devices.get_device_types()


@router.get("/get_example_config/{device_name}", responses=config_responses)
async def get_example_config(device_name: str):
    try:
        return await devices.get_example_config(device_name)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": "Internal Error"})


@router.post("/create_device/{device_name}")
async def create_device(device_name: str, data: dict):
    try:
        return await devices.create_device(data, device_name)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": "Internal Error"})


@router.put("/update_device/{device_name}")
async def update_device(device_name: str, data: dict):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return await devices.update_device(data, device_name)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": "Internal Error"})


@router.delete("/delete_device/{device_name}")
async def delete_device(device_name: str):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return await devices.delete_device(name=device_name)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": "Internal Error"})
