from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.core import settings, templates

router = APIRouter(prefix='', tags=['Pages'])


@router.get('/settings/application', response_class=HTMLResponse)
async def settings_page(request: Request):
	return templates.TemplateResponse(
		'pages/application_settings/main.html',
		{'request': request, 'title': 'Settings', 'alerts': []},
		media_type='text/html; charset=utf-8',
	)

@router.get('/settings/devices', response_class=HTMLResponse)
async def devices_page(request: Request):
	return templates.TemplateResponse(
		'pages/devices_settings/main.html',
		{'request': request, 'title': 'Settings', 'alerts': []},
		media_type='text/html; charset=utf-8',
	)
