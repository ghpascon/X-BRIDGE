from pathlib import Path
from datetime import datetime, timedelta
import logging
import os
from app.core.config import settings

# Cria diretório de logs
log_dir = Path(settings.LOG_PATH)
log_dir.mkdir(exist_ok=True)

# Apaga logs com mais de settings.STORAGE_DAYS dias
cutoff_date = datetime.now() - timedelta(days=settings.STORAGE_DAYS)
for log_path in log_dir.glob("*.log"):
    try:
        # Extrai a data do nome do arquivo ignorando sufixos (_info ou _error)
        # Exemplo de nome: "2025-05-19_info.log"
        date_part = log_path.stem.split('_')[0]  # Pega só o "2025-05-19"
        file_date = datetime.strptime(date_part, "%Y-%m-%d")
        if file_date < cutoff_date:
            os.remove(log_path)
            print(f"Removido log antigo: {log_path}")
    except Exception:
        # Ignora arquivos com nomes que não correspondem ao formato esperado
        pass

# Define arquivos de log separados
today_str = datetime.now().strftime("%Y-%m-%d")
info_log_file = log_dir / f"{today_str}_info.log"
error_log_file = log_dir / f"{today_str}_error.log"

# Formatação do log
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

# Logger principal
logger = logging.getLogger("simple_logger")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Filtros personalizados
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO and record.levelno < logging.ERROR

class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR

if not logger.handlers:
    # Handler para logs INFO (e WARNING)
    info_handler = logging.FileHandler(info_log_file, encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(InfoFilter())
    logger.addHandler(info_handler)

    # Handler para logs ERROR (e CRITICAL)
    error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(ErrorFilter())
    logger.addHandler(error_handler)

    # Handler para console (DEBUG e acima)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Funções utilitárias para log
log_info = logger.info
log_error = logger.error
