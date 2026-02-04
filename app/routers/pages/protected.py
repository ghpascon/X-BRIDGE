from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

router = APIRouter(prefix='', tags=['Pages'])


@router.get('/protected_page', response_class=HTMLResponse)
async def protected_page(request: Request):
	return templates.TemplateResponse(
		'pages/protected_page/main.html',
		{'request': request, 'title': 'Protected', 'alerts': []},
		media_type='text/html; charset=utf-8',
	)
