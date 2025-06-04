from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.path import get_path

import os
import importlib
import asyncio
from contextlib import asynccontextmanager
from app.async_func import create_tasks

from app.schemas.logger import log_info, log_error

def include_all_routes(current_path):
    routes_path = os.path.join(os.path.dirname(__file__), get_path(current_path))

    for filename in os.listdir(routes_path):
        if not filename == "__pycache__" and not "." in filename:
            include_all_routes(current_path + '/' + filename)
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            file_path = os.path.join(routes_path, filename)

            spec = importlib.util.spec_from_file_location(f"app.routes.{module_name}", file_path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "router"):
                    app.include_router(module.router)
                    print(f"✅ Rota incluída: {module_name}")
                else:
                    log_error(f"⚠️  Arquivo {filename} não contém um 'router'")
            except Exception as e:
                log_error(f"❌ Erro ao importar {filename}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = await create_tasks(get_path("app/async_func"))
    try:
        yield  
    except Exception as e:
        print(f"Erro durante o lifespan: {e}")
    finally:
        for t in tasks:
            t.cancel()
        for i, t in enumerate(tasks, start=1):
            try:
                await t
            except asyncio.CancelledError:
                print(f"Tarefa {i} finalizada com sucesso.")
            except Exception as e:
                print(f"Erro ao cancelar a tarefa {i}: {e}")

app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",           # Nome do cookie
    https_only=True,                    # Garante HTTPS (ideal em produção)
    same_site="lax",                    # Proteção contra CSRF básica
    max_age=3600                        # Tempo de vida da sessão em segundos
)

app.mount("/static", StaticFiles(directory=get_path("app/static")), name="static")

include_all_routes("app/routes")
log_info("Aplicação iniciada")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://localhost:5000")
    threading.Timer(1.0, open_browser).start()

    uvicorn.run(app, host="0.0.0.0", port=5000)
    
# python -m app.db.database
# python -m uvicorn main:app --reload
# python -m uvicorn main:app --host 0.0.0.0 --port $PORT






       
