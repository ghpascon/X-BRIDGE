from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import logger
from app.core.templates import templates

router = APIRouter(prefix="", tags=["Logs"])


@router.get("/logs", response_class=HTMLResponse)
async def logs(request: Request):
    return templates.TemplateResponse(
        "logs/main.html",
        {"request": request, "title": "Logs"},
        media_type="text/html; charset=utf-8",
    )


@router.get("/get_logs")
async def get_logs():
    return list(logger.logs)
