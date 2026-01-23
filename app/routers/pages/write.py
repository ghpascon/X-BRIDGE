from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

router = APIRouter(prefix='', tags=['Pages'])


@router.get('/write_page', response_class=HTMLResponse)
async def write_page(request: Request):
	return templates.TemplateResponse(
		'pages/write_page/main.html',
		{'request': request, 'title': 'Write Tags', 'alerts': []},
		media_type='text/html; charset=utf-8',
	)
