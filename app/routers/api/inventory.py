import asyncio
from typing import List, Union

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.models import EventRequest, TagRequest, validate_device
from app.schemas.api.responses import device_responses, gpo_responses, state_responses
from app.schemas.events import events

router = APIRouter(prefix=get_prefix_from_path(__file__), tags=[get_prefix_from_path(__file__)])

from app.schemas.devices import devices


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


@router.get(
    "/get_tags",
    summary="Get Current RFID Tags",
    description="Retrieve all currently detected RFID tags from all connected readers",
    response_description="List of RFID tag objects with their metadata",
)
async def get_tags():
    return [tag for tag in events.tags.values()]


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


@router.post("/clear/{device}")
async def clear_tags(device: str):
    print(f"CLEAR -> {device}")
    await devices.clear_tags(device)
    return {"msg": f"{device} clear tags"}


@router.post(
    "/clear_all_tags",
    responses=device_responses,
    summary="Clear tags from all devices",
    description="Clears the tag lists from all connected devices.",
)
async def clear_all_tags():
    try:
        await devices.clear_tags()
        return {"msg": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
