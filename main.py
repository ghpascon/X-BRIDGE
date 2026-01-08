"""
SMARTX RFID Middleware - Main Application Entry Point

This module initializes and configures the FastAPI application, sets up middleware,
exception handlers, and starts the web server when executed directly.

Para executar a aplicação:
    poetry run python main.py

Para configurar MySQL:
    Configure a URL de conexão no arquivo config/config.json:
    "DATABASE_URL": "sqlite+aiosqlite:///instance/db.sqlite",
    "DATABASE_URL": "mysql+aiomysql://root:admin@localhost:3306/middleware_smartx"
"""

import sys

sys.coinit_flags = 0
import asyncio

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
import os
import threading
import webbrowser
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.async_func import create_tasks
from app.core import settings
from app.core.exeption_handlers import setup_exeptions
from app.core.middleware import setup_middlewares
from app.core.path import get_path, include_all_routers

# Application constants
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"
SESSION_MAX_AGE = 3600  # 1 hour in seconds
SWAGGER_FILE_PATH = "SWAGGER.md"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the asynchronous lifecycle of the application.

    This context manager handles startup and shutdown processes:
    - On startup: Creates and starts background tasks
    - On shutdown: Cancels all running background tasks

    Args:
        app: The FastAPI application instance
    """
    logging.info("Starting application lifecycle")
    tasks: List[asyncio.Task] = []

    try:
        # Initialize background tasks
        tasks = await create_tasks(get_path("app/async_func"))
        logging.info(f"Started {len(tasks)} background tasks")
        yield
    except Exception as e:
        logging.error(f"Critical error during application lifecycle: {e}", exc_info=True)
    finally:
        # Ensure all background tasks are properly cancelled at shutdown
        logging.info("Shutting down application, cancelling background tasks")
        for task in tasks:
            if not task.done():
                task.cancel()

        if tasks:
            # Wait for all tasks to finish cancellation
            await asyncio.gather(*tasks, return_exceptions=True)
        logging.info("Application shutdown complete")


def load_swagger_description() -> str:
    """
    Load the Swagger description in markdown format from a file.

    Returns:
        The markdown content as a string, or a default message if the file is missing
    """
    try:
        with open(SWAGGER_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.warning(f"{SWAGGER_FILE_PATH} not found. Using default description.")
        return "Documentation not found."
    except Exception as e:
        logging.error(f"Error loading Swagger documentation: {e}")
        return "Error loading API documentation."


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function:
    1. Loads the Swagger documentation
    2. Creates the FastAPI instance
    3. Configures middleware
    4. Registers exception handlers
    5. Mounts static files
    6. Includes all routers

    Returns:
        Configured FastAPI application instance
    """
    # Load API documentation
    markdown_description = load_swagger_description()

    # Create FastAPI instance
    app = FastAPI(
        lifespan=lifespan,
        title=settings.data.get("TITLE", "SMARTX"),
        description=markdown_description,
        redoc_url=None,
        docs_url=None,
    )

    # Configure session middleware
    secret_key = settings.data.get("SECRET_KEY")
    if not secret_key:
        logging.warning("SECRET_KEY not found in settings. Using default fallback.")
        secret_key = "smartx_default_secret_key"  # Fallback value

    setup_exeptions(app)
    setup_middlewares(app)

    # Mount static files directory
    static_dir = get_path("app/static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    else:
        logging.warning(f"Static files directory not found: {static_dir}")

    # Include all routers from routers directory
    include_all_routers("app/routers", app)
    logging.info("Application successfully configured")

    return app


# Create the FastAPI application instance
app = create_application()

# Server startup code
if __name__ == "__main__":
    # Get port and host from settings or use defaults
    port = settings.data.get("PORT", DEFAULT_PORT)
    host = settings.data.get("HOST", DEFAULT_HOST)

    logging.info(f"Starting server on {host}:{port}")

    # Open browser automatically if configured
    if settings.data.get("OPEN_BROWSER", True):

        def open_browser() -> None:
            """Open the default web browser at the application URL."""
            url = f"http://localhost:{port}"
            logging.info(f"Opening browser at {url}")
            webbrowser.open_new(url)

        # Delay opening browser to allow server startup
        threading.Timer(1.0, open_browser).start()

    # Start uvicorn server
    try:
        uvicorn.run(
            app, host=host, port=port, access_log=False, log_level="critical", log_config=None
        )
    except SystemExit as e:
        logging.error(f"Server exited with SystemExit: {e}")
        error_html = get_path("app/templates/start_error.html")
        url = f"file://{error_html}"
        webbrowser.open_new(url)

    except Exception as e:
        logging.error(f"Failed to start server: {e}")
