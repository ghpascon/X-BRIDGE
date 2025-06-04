from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from app.core.templates import templates  

router = APIRouter(prefix="", tags=["Root"])

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, msg:str=None, classe:str="alert-primary"):
    alerts=[]

    if msg is not None and not len(msg) == 0:
        alert = {
            "text":msg,
            "class":classe
        }
        alerts.append(alert)  

    return templates.TemplateResponse("root/index.html", {
        "request": request,
        "title": "CHECKBOX",
        "alerts":alerts,
    })
