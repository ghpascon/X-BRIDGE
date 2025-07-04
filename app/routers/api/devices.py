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


@router.get(
    "/get_device_list",
    responses=device_list_responses,
    summary="Get all device names",
    description="Returns a list of all registered device names."
)
async def api_get_device_list():
    return devices.get_device_list()


@router.get(
    "/get_device_config/{device_name}",
    responses=config_responses,
    summary="Get device configuration",
    description="Returns the current configuration of the specified device."
)
async def get_device_config(device_name: str):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return devices.devices.get(device_name).config
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/get_device_types_list",
    responses=device_list_responses,
    summary="Get list of supported device types",
    description="Returns a list of supported device types that can be configured."
)
async def api_get_device_types_list():
    return await devices.get_device_types()


@router.get(
    "/get_example_config/{device_name}",
    responses=config_responses,
    summary="Get example config for a device type",
    description="Returns an example configuration for a given device type."
)
async def get_example_config(device_name: str):
    try:
        return await devices.get_example_config(device_name)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/create_device/{device_name}",
    summary="Create a new device",
    description="Creates a new device with the given name and configuration."
)
async def create_device(device_name: str, data: dict):
    try:
        return await devices.create_device(data, device_name)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/update_device/{device_name}",
    summary="Update an existing device",
    description="Updates the configuration of an existing device."
)
async def update_device(device_name: str, data: dict):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return await devices.update_device(data, device_name)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/delete_device/{device_name}",
    summary="Delete a device",
    description="Deletes the specified device from the system."
)
async def delete_device(device_name: str):
    try:
        status, msg = validate_device(device=device_name, need_connected=False)
        if not status:
            raise HTTPException(status_code=422, detail=msg)
        return await devices.delete_device(name=device_name)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
