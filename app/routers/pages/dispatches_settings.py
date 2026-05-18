from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routers.pages import router as pages_router


templates = Jinja2Templates(directory='app/templates')

router = APIRouter()


@router.get('/dispatches_settings', response_class=HTMLResponse)
def dispatches_settings(request: Request):
	return templates.TemplateResponse('pages/dispatches_settings/main.html', {'request': request})


# Register this router in your main pages router if not already
pages_router.include_router(router)
