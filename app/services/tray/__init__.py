from ._main import TrayManager
from app.core import settings

tray_manager = TrayManager(
    app_name=settings.TITLE,
    icon_path="config/logo.ico"
)