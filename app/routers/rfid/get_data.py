from fastapi import APIRouter, Request

from app.core.path import get_prefix_from_path
from app.db.database import database_engine
from app.schemas.devices import devices
from app.schemas.rfid import rfid

router = APIRouter(
    prefix=get_prefix_from_path(__file__), tags=[get_prefix_from_path(__file__)]
)


@router.get("/get_tags")
async def get_tags():
    tags_info = []
    current_tags = dict(rfid.tags)  # Cópia do dicionário atual

    total = {
        "timestamp": "Total",
        "device": "",
        "epc": "",
        "tid": "",
        "ant": "",
        "rssi": len(current_tags),
    }
    tags_info.append(total)

    for tag in current_tags:
        tag_data = current_tags.get(tag)
        if tag_data is None:
            continue
        current_tag = {
            "timestamp": tag_data.get("timestamp"),
            "device": tag_data.get("device"),
            "epc": tag_data.get("epc"),
            "tid": tag_data.get("tid"),
            "ant": tag_data.get("ant"),
            "rssi": tag_data.get("rssi"),
        }
        tags_info.append(current_tag)

    return tags_info


@router.get("/get_events")
async def get_events():
    return list(rfid.events)


@router.get("/reader_state/{device}")
async def get_reader_state(request: Request, device: str):
    if device not in devices.devices:
        return -1

    reader = devices.devices[device]

    if not reader.is_connected:
        state = 0
    elif hasattr(reader, "is_reading") and reader.is_reading:
        state = 2
    else:
        state = 1

    return {"state": state}


@router.get("/get_report")
async def get_report(request: Request):
    return await database_engine.get_report()
