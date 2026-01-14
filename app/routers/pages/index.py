from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.core import settings, templates

router = APIRouter(prefix='', tags=['Pages'])


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
	alerts = []
	# alerts example
	# alerts = [
	# 	{'text': 'Sistema SMARTX RFID iniciado com sucesso!', 'level': 'success'},
	# 	{'text': 'Conectado aos dispositivos RFID', 'level': 'info'},
	# 	{'text': 'Atenção: Verifique a configuração dos devices', 'level': 'warning'},
	# 	{'text': 'Erro de conexão detectado', 'level': 'error'},
	# ]
	return templates.TemplateResponse(
		'pages/index/main.html',
		{'request': request, 'title': settings.TITLE, 'alerts': alerts},
		media_type='text/html; charset=utf-8',
	)


@router.get('/docs', include_in_schema=False)
async def docs():
	return get_swagger_ui_html(
		openapi_url='/openapi.json',
		title=settings.TITLE + ' - Docs',
		swagger_js_url='/static/docs/swagger-ui-bundle.js',
		swagger_css_url='/static/docs/swagger-ui.css',
		swagger_favicon_url='/static/images/logo.png',
	)
