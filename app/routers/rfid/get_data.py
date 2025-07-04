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
        "device": "Total",
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
            "device": tag_data.get("device"),
            "epc": tag_data.get("epc"),
            "tid": tag_data.get("tid"),
            "ant": tag_data.get("ant"),
            "rssi": tag_data.get("rssi"),
        }
        tags_info.append(current_tag)

    return tags_info


@router.get("/reader_state/{device}")
async def get_reader_state(request: Request, device: str):
    if device not in devices.devices:
        return {"state": f"❌ Device '{device}' not found"}

    if not devices.devices[device].is_connected:
        state = "❌ Reader disconnected"
    elif devices.devices[device].is_reading:
        state = "🔍 Reading tags"
    else:
        state = "🛑 Waiting for reading..."
    return {"state": state}

@router.get("/get_report")
async def get_report(request: Request):
    return await database_engine.get_report()
