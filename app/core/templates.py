from datetime import datetime

from fastapi.templating import Jinja2Templates

from ..core.path import get_path
from ..schemas.devices import devices


def generate_footer():
    year = datetime.now().year
    return f"© {year} - SMARTX"


templates = Jinja2Templates(directory=get_path("app/templates"))
templates.env.globals["generate_footer"] = generate_footer
templates.env.globals["device_list"] = devices.get_device_list
templates.env.globals["is_rfid_reader"] = devices.is_rfid_reader
