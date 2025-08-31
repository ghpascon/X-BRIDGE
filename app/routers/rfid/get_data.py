from fastapi import APIRouter, Request

from app.core.path import get_prefix_from_path
from app.db.database import database_engine
from app.routers.api.inventory import get_tags
from app.schemas.devices import devices
from app.schemas.events import events

router = APIRouter(prefix=get_prefix_from_path(__file__), tags=[get_prefix_from_path(__file__)])


@router.get("/table_tags")
async def table_tags():
    tags = await get_tags()
    if len(tags) > 0:
        first_tag = tags[0]
        total = {}

        for i, key in enumerate(first_tag.keys()):
            if i == 0:
                total[key] = "Total"
            elif i == len(first_tag.keys()) - 1:
                total[key] = len(tags)
            else:
                total[key] = ""
    else:
        total = {"Total": "", "count": 0}

    result = [total] + tags
    return result
