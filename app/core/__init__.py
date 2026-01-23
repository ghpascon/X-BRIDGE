from .config import Settings
from smartx_rfid.utils.logger_manager import LoggerManager
import os
from .build_templates import TemplateManager
from .indicator import Indicator

# DEFAULT VARS
FILES_PATH = 'config'
SWAGGER_PATH = 'SWAGGER.md'
CONFIG_PATH = f'{FILES_PATH}/config.json'
TEMPLATES_PATH = 'app/templates'
DEVICES_PATH = f'{FILES_PATH}/devices'
ICON_PATH = f'{FILES_PATH}/logo.ico'
EXAMPLE_PATH = 'examples'

##CONFIG APLICATION
# settings
settings = Settings(CONFIG_PATH)

# logging
logger = LoggerManager(
	log_path=settings.LOG_PATH,
	storage_days=settings.STORAGE_DAYS,
	base_filename=os.path.basename(os.getcwd()),
)

# templates
templates = TemplateManager(TEMPLATES_PATH).templates
