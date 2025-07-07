import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.async_func import create_tasks
from app.core.config import settings
from app.core.path import get_path, include_all_routers


# Async lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = await create_tasks(get_path("app/async_func"))
    try:
        yield
    except Exception as e:
        logging.error(f"Error during lifespan: {e}")
    finally:
        for t in tasks:
            t.cancel()
        for i, t in enumerate(tasks, start=1):
            try:
                await t
            except asyncio.CancelledError:
                print(f"Task {i} successfully cancelled.")
            except Exception as e:
                print(f"Error while cancelling task {i}: {e}")

# Load Swagger markdown description
with open("SWAGGER.md", "r", encoding="utf-8") as f:
    markdown_description = f.read()

# FastAPI app instance
app = FastAPI(
    lifespan=lifespan,
    title="RFID Middleware",
    description=markdown_description
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.data.get("SECRET_KEY"),
    session_cookie="session",
    https_only=True,        # Recommended for production
    same_site="lax",        # Basic CSRF protection
    max_age=3600            # Session lifetime (seconds)
)

# Global 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return RedirectResponse(url=request.app.url_path_for("index"))

# Static files
app.mount("/static", StaticFiles(directory=get_path("app/static")), name="static")

# Include routers
include_all_routers("app/routers", app)
logging.info("✅ Application started successfully.")

# Uvicorn startup
if __name__ == "__main__":
    import uvicorn

    # Optional: Open browser automatically
    # import webbrowser
    # import threading
    # def open_browser():
    #     webbrowser.open_new("http://localhost:5000")
    # threading.Timer(1.0, open_browser).start()

    uvicorn.run(app, host="0.0.0.0", port=5000)
